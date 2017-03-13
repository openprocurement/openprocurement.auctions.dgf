# -*- coding: utf-8 -*-
import logging
from iso8601 import parse_date
from openprocurement.api.models import get_now, TZ
from openprocurement.api.utils import calculate_business_date
from openprocurement.api.traversal import Root
from barbecue import chef
from uuid import uuid4

from openprocurement.auctions.dgf.models import VERIFY_AUCTION_PROTOCOL_TIME, AWARD_PAYMENT_TIME, CONTRACT_SIGNING_TIME
from openprocurement.auctions.dgf.utils import invalidate_bids_under_threshold

LOGGER = logging.getLogger(__name__)
SCHEMA_VERSION = 1
SCHEMA_DOC = 'openprocurement_auctions_dgf_schema'


def get_db_schema_version(db):
    schema_doc = db.get(SCHEMA_DOC, {"_id": SCHEMA_DOC})
    return schema_doc.get("version", SCHEMA_VERSION - 1)


def set_db_schema_version(db, version):
    schema_doc = db.get(SCHEMA_DOC, {"_id": SCHEMA_DOC})
    schema_doc["version"] = version
    db.save(schema_doc)


def migrate_data(registry, destination=None):
    if registry.settings.get('plugins') and 'auctions.dgf' not in registry.settings['plugins'].split(','):
        return
    cur_version = get_db_schema_version(registry.db)
    if cur_version == SCHEMA_VERSION:
        return cur_version
    for step in xrange(cur_version, destination or SCHEMA_VERSION):
        LOGGER.info("Migrate openprocurement auction schema from {} to {}".format(step, step + 1), extra={'MESSAGE_ID': 'migrate_data'})
        migration_func = globals().get('from{}to{}'.format(step, step + 1))
        if migration_func:
            migration_func(registry)
        set_db_schema_version(registry.db, step + 1)


def switch_auction_to_unsuccessful(auction):
    actual_award = [a for a in auction["awards"] if a['status'] in ['active', 'pending']][0]
    if auction['status'] == 'active.awarded':
        for i in auction['contracts']:
            if i['awardID'] == actual_award['id']:
                i['status'] = 'cancelled'
    actual_award['status'] = 'unsuccessful'
    auction['awardPeriod']['endDate'] = actual_award['complaintPeriod']['endDate'] = get_now().isoformat()
    auction['status'] = 'unsuccessful'


def from0to1(registry):
    class Request(object):
        def __init__(self, registry):
            self.registry = registry

    results = registry.db.iterview('auctions/all', 2 ** 10, include_docs=True)

    request = Request(registry)
    root = Root(request)

    docs = []
    for i in results:
        auction = i.doc
        if auction['procurementMethodType'] not in ['dgfOtherAssets', 'dgfFinancialAssets'] \
                or auction['status'] not in ['active.qualification', 'active.awarded'] \
                or 'awards' not in auction:
            continue

        now = get_now().isoformat()
        awards = auction["awards"]
        unique_awards = len(set([a['bid_id'] for a in awards]))

        if unique_awards > 2:
            switch_auction_to_unsuccessful(auction)
        else:
            invalidate_bids_under_threshold(auction)
            if all(bid['status'] == 'invalid' for bid in auction['bids']):
                switch_auction_to_unsuccessful(auction)

        if auction['status'] != 'unsuccessful':
            award = [a for a in auction["awards"] if a['status'] in ['active', 'pending']][0]

            award_create_date = award['complaintPeriod']['startDate']

            periods = {
                'verificationPeriod': {
                    'startDate': award_create_date,
                    'endDate': award_create_date
                },
                'paymentPeriod': {
                    'startDate': award_create_date,
                    'endDate': calculate_business_date(parse_date(award_create_date, TZ), AWARD_PAYMENT_TIME, auction, True).isoformat()
                },
                'signingPeriod': {
                    'startDate': award_create_date,
                    'endDate': calculate_business_date(parse_date(award_create_date, TZ), CONTRACT_SIGNING_TIME, auction, True).isoformat()
                }
            }

            award.update(periods)

            if award['status'] == 'pending':
                award['status'] = 'pending.payment'

            elif award['status'] == 'active':
                award['verificationPeriod']['endDate'] = award['paymentPeriod']['endDate'] = now

            if unique_awards == 1:
                bid = chef(auction['bids'], auction.get('features'), [], True)[1]

                award = {
                    'id': uuid4().hex,
                    'bid_id': bid['id'],
                    'status': 'pending.waiting',
                    'date': awards[0]['date'],
                    'value': bid['value'],
                    'suppliers': bid['tenderers'],
                    'complaintPeriod': {
                        'startDate': awards[0]['date']
                    }
                }
                if bid['status'] == 'invalid':
                    award['status'] == 'unsuccessful'
                    award['complaintPeriod']['endDate'] = now

                awards.append(award)

        model = registry.auction_procurementMethodTypes.get(auction['procurementMethodType'])
        if model:
            try:
                auction = model(auction)
                auction.__parent__ = root
                auction = auction.to_primitive()
            except:
                LOGGER.error("Failed migration of auction {} to schema 1.".format(auction.id), extra={'MESSAGE_ID': 'migrate_data_failed', 'AUCTION_ID': auction.id})
            else:
                auction['dateModified'] = get_now().isoformat()
                docs.append(auction)
        if len(docs) >= 2 ** 7:
            registry.db.update(docs)
            docs = []
    if docs:
        registry.db.update(docs)
