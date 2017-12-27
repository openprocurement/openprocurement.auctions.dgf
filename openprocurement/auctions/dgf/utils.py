# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from barbecue import chef
from openprocurement.api.models import get_now, TZ
from openprocurement.api.utils import (
    upload_file as base_upload_file,
    get_file as base_get_file,
    DOCUMENT_BLACKLISTED_FIELDS,
    context_unpack
)
from openprocurement.auctions.core.utils import (
    cleanup_bids_for_cancelled_lots, check_complaint_status,
    remove_draft_bids,
)
from openprocurement.auctions.core.constants import (
    DOCUMENT_TYPE_URL_ONLY,
    DOCUMENT_TYPE_OFFLINE
)
from openprocurement.auctions.core.contracting.dgf.utils import (
    check_auction_status
)
PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def upload_file(request, blacklisted_fields=DOCUMENT_BLACKLISTED_FIELDS):
    first_document = request.validated['documents'][0] if 'documents' in request.validated and request.validated['documents'] else None
    if 'data' in request.validated and request.validated['data']:
        document = request.validated['document']
        if document.documentType in (DOCUMENT_TYPE_URL_ONLY + DOCUMENT_TYPE_OFFLINE):
            if first_document:
                for attr_name in type(first_document)._fields:
                    if attr_name not in blacklisted_fields:
                        setattr(document, attr_name, getattr(first_document, attr_name))
            if document.documentType in DOCUMENT_TYPE_OFFLINE:
                document.format = 'offline/on-site-examination'
            return document
    return base_upload_file(request, blacklisted_fields)


def get_file(request):
    document = request.validated['document']
    if document.documentType in DOCUMENT_TYPE_URL_ONLY:
        request.response.status = '302 Moved Temporarily'
        request.response.location = document.url
        return document.url
    return base_get_file(request)


def check_bids(request):
    auction = request.validated['auction']
    if auction.lots:
        [setattr(i.auctionPeriod, 'startDate', None) for i in auction.lots if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate]
        [setattr(i, 'status', 'unsuccessful') for i in auction.lots if i.numberOfBids < 2 and i.status == 'active']
        cleanup_bids_for_cancelled_lots(auction)
        if not set([i.status for i in auction.lots]).difference(set(['unsuccessful', 'cancelled'])):
            auction.status = 'unsuccessful'
    else:
        if auction.numberOfBids < 2:
            if auction.auctionPeriod and auction.auctionPeriod.startDate:
                auction.auctionPeriod.startDate = None
            auction.status = 'unsuccessful'


def check_status(request):
    auction = request.validated['auction']
    now = get_now()
    for complaint in auction.complaints:
        check_complaint_status(request, complaint, now)
    for award in auction.awards:
        check_award_status(request, award, now)
        for complaint in award.complaints:
            check_complaint_status(request, complaint, now)
    if not auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        LOGGER.info('Switched auction {} to {}'.format(auction['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_active.auction'}))
        auction.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        if auction.numberOfBids < 2 and auction.auctionPeriod:
            auction.auctionPeriod.startDate = None
        return
    elif auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        LOGGER.info('Switched auction {} to {}'.format(auction['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_active.auction'}))
        auction.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        [setattr(i.auctionPeriod, 'startDate', None) for i in auction.lots if i.numberOfBids < 2 and i.auctionPeriod]
        return
    elif not auction.lots and auction.status == 'active.awarded':
        standStillEnds = [
            a.complaintPeriod.endDate.astimezone(TZ)
            for a in auction.awards
            if a.complaintPeriod.endDate
        ]
        if not standStillEnds:
            return
        standStillEnd = max(standStillEnds)
        if standStillEnd <= now:
            check_auction_status(request)
    elif auction.lots and auction.status in ['active.qualification', 'active.awarded']:
        if any([i['status'] in auction.block_complaint_status and i.relatedLot is None for i in auction.complaints]):
            return
        for lot in auction.lots:
            if lot['status'] != 'active':
                continue
            lot_awards = [i for i in auction.awards if i.lotID == lot.id]
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in lot_awards
                if a.complaintPeriod.endDate
            ]
            if not standStillEnds:
                continue
            standStillEnd = max(standStillEnds)
            if standStillEnd <= now:
                check_auction_status(request)
                return


def check_award_status(request, award, now):
    auction = request.validated['auction']
    if (award.status == 'pending.verification' and award['verificationPeriod']['endDate'] < now) or \
            (award.status == 'pending.payment' and award['paymentPeriod']['endDate'] < now) or \
            (award.status == 'active' and award['signingPeriod']['endDate'] < now):
        if award.status == 'active':
            auction.awardPeriod.endDate = None
            auction.status = 'active.qualification'
            for contract in auction.contracts:
                if contract.awardID == award.id:
                    contract.status = 'cancelled'
        award.status = 'unsuccessful'
        award.complaintPeriod.endDate = now
        switch_to_next_award(request)


def invalidate_bids_under_threshold(auction):
    value_threshold = round(auction['value']['amount'] + auction['minimalStep']['amount'], 2)
    for bid in auction['bids']:
        if bid['value']['amount'] < value_threshold:
            bid['status'] = 'invalid'


def create_awards(request):
    auction = request.validated['auction']
    auction.status = 'active.qualification'
    now = get_now()
    auction.awardPeriod = type(auction).awardPeriod({'startDate': now})

    bids = chef(auction.bids, auction.features or [], [], True)

    for i, status in enumerate(['pending.verification', 'pending.waiting']):
        bid = bids[i].serialize()
        award = type(auction).awards.model_class({
            '__parent__': request.context,
            'bid_id': bid['id'],
            'status': status,
            'date': now,
            'value': bid['value'],
            'suppliers': bid['tenderers'],
            'complaintPeriod': {'startDate': now}
        })
        if bid['status'] == 'invalid':
            award.status = 'unsuccessful'
            award.complaintPeriod.endDate = now
        if award.status == 'pending.verification':
            award.signingPeriod = award.paymentPeriod = award.verificationPeriod = {'startDate': now}
            request.response.headers['Location'] = request.route_url('{}:Auction Awards'.format(auction.procurementMethodType), auction_id=auction.id, award_id=award['id'])
        auction.awards.append(award)


def switch_to_next_award(request):
    auction = request.validated['auction']
    now = get_now()
    waiting_awards = [i for i in auction.awards if i['status'] == 'pending.waiting']
    if waiting_awards:
        award = waiting_awards[0]
        award.status = 'pending.verification'
        award.signingPeriod = award.paymentPeriod = award.verificationPeriod = {'startDate': now}
        award = award.serialize()
        request.response.headers['Location'] = request.route_url('{}:Auction Awards'.format(auction.procurementMethodType), auction_id=auction.id, award_id=award['id'])

    elif all([award.status in ['cancelled', 'unsuccessful'] for award in auction.awards]):
        auction.awardPeriod.endDate = now
        auction.status = 'unsuccessful'


def check_auction_protocol(award):
    if award.documents:
        for document in award.documents:
            if document['documentType'] == 'auctionProtocol' and document['author'] == 'auction_owner':
                return True
    return False
