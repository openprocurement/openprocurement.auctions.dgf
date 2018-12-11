# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution

from openprocurement.auctions.core.plugins.contracting.base.utils import (
    check_auction_status
)
from openprocurement.auctions.core.utils import (
    TZ,
    check_complaint_status,
    cleanup_bids_for_cancelled_lots,
    get_now,
    remove_draft_bids,
    log_auction_status_change
)
from openprocurement.auctions.core.interfaces import IAuctionManager


PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def check_bids(request):
    auction = request.validated['auction']
    adapter = request.registry.getAdapter(auction, IAuctionManager)
    if auction.lots:
        [setattr(i.auctionPeriod, 'startDate', None) for i in auction.lots if i.numberOfBids < 2 and i.auctionPeriod and i.auctionPeriod.startDate]
        [setattr(i, 'status', 'unsuccessful') for i in auction.lots if i.numberOfBids < 2 and i.status == 'active']
        cleanup_bids_for_cancelled_lots(auction)
        if not set([i.status for i in auction.lots]).difference(set(['unsuccessful', 'cancelled'])):
            adapter.pendify_auction_status('unsuccessful')
    else:
        if auction.numberOfBids < 2:
            if auction.auctionPeriod and auction.auctionPeriod.startDate:
                auction.auctionPeriod.startDate = None
            adapter.pendify_auction_status('unsuccessful')


def check_status(request):
    auction = request.validated['auction']
    now = get_now()
    for complaint in auction.complaints:
        check_complaint_status(request, complaint, now)
    for award in auction.awards:
        request.content_configurator.check_award_status(request, award, now)
        for complaint in award.complaints:
            check_complaint_status(request, complaint, now)
    if not auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        auction.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        log_auction_status_change(request, auction, auction.status)
        if auction.numberOfBids < 2 and auction.auctionPeriod:
            auction.auctionPeriod.startDate = None
        return
    elif auction.lots and auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        auction.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        log_auction_status_change(request, auction, auction.status)
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
