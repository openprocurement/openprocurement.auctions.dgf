# -*- coding: utf-8 -*-
import unittest

from uuid import uuid4
from copy import deepcopy

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.migration_blanks import migrate
from openprocurement.auctions.core.plugins.awarding.v3.tests.migration import (
    MigrateAwardingV2toV3Mixin
)

from openprocurement.auctions.dgf.migration import (
    migrate_data, set_db_schema_version, SCHEMA_VERSION, get_db_schema_version
)
from openprocurement.auctions.dgf.tests.base import (
    BaseWebTest, BaseAuctionWebTest, test_bids
)
from openprocurement.auctions.dgf.tests.blanks.migration_blanks import (
    # MigrateTestFrom1To2InvalidBids
    migrate_one_pending_bids,
    migrate_one_active_bids,
    migrate_unsuccessful_pending_bids,
    migrate_unsuccessful_active_bids,
    # MigrateTestFrom1To2InvalidBid
    migrate_one_pending_bid,
    migrate_one_active_bid,
    migrate_unsuccessful_pending_bid,
    migrate_unsuccessful_active_bid,
    # MigrateTestFrom1To2WithTwoBids
    migrate_pending_to_unsuccesful,
    migrate_pending_to_complete,
    migrate_active_to_unsuccessful,
    migrate_active_to_complete,
    migrate_cancelled_pending_to_complete,
    migrate_unsuccessful_pending_to_complete,
    migrate_unsuccessful_active_to_complete,
    migrate_cancelled_unsuccessful_pending,
    migrate_cancelled_unsuccessful_cancelled_pending_to_unsuccessful,
    migrate_cancelled_unsuccessful_cancelled_active_to_unsuccessful,
    # MigrateTestFrom1To2WithThreeBids
    migrate_unsuccessful_unsuccessful_pending,
    migrate_unsuccessful_unsuccessful_active,
    # MigrateTestFrom1To2SuspendedAuction
    migrate_pending,
    migrate_active,
    # MigrateTestFrom1To2SuspendedAuctionWithInvalidBids
    migrate_one_pending_suspend_bids,
    migrate_one_active_suspend_bids,
    migrate_unsuccessful_pending_suspend_bids,
    migrate_unsuccessful_active_suspend_bids,
    # MigrateTestFrom1To2SuspendedAuctionWithInvalidBid
    migrate_one_pending_suspend_bid,
    migrate_one_active_suspend_bid,
    migrate_unsuccessful_pending_suspend_bid,
    migrate_unsuccessful_active_suspend_bid
)


class MigrateTest(BaseWebTest):
    migrate_data = staticmethod(migrate_data)
    get_db_schema_version = staticmethod(get_db_schema_version)
    schema_version = SCHEMA_VERSION

    def setUp(self):
        super(MigrateTest, self).setUp()
        migrate_data(self.app.app.registry)

    test_migrate = snitch(migrate)

# @unittest.skipIf(AWARDING_OF_PROCUREMENT_METHOD_TYPE['dgfOtherAssets'] != 'awarding_2_0', "Awarding 3.0 used")
# class MigrateTestFrom1To2InvalidBids(BaseAuctionWebTest):
#     initial_status = 'active.qualification'
#     initial_bids = test_bids
#
#     def setUp(self):
#         super(MigrateTestFrom1To2InvalidBids, self).setUp()
#         migrate_data(self.app.app.registry)
#         set_db_schema_version(self.db, 0)
#         auction = self.db.get(self.auction_id)
#         for bid in auction['bids']:
#             bid['value']['amount'] = auction['value']['amount']
#         self.db.save(auction)
#
#     test_migrate_one_pending_bids = snitch(migrate_one_pending_bids)
#     test_migrate_one_active_bids = snitch(migrate_one_active_bids)
#     test_migrate_unsuccessful_pending_bids = snitch(migrate_unsuccessful_pending_bids)
#     test_migrate_unsuccessful_active_bids = snitch(migrate_unsuccessful_active_bids)
#
#
# @unittest.skipIf(AWARDING_OF_PROCUREMENT_METHOD_TYPE['dgfOtherAssets'] != 'awarding_2_0', "Awarding 3.0 used")
# class MigrateTestFrom1To2InvalidBid(BaseAuctionWebTest):
#     initial_status = 'active.qualification'
#     initial_bids = test_bids
#
#     def setUp(self):
#         super(MigrateTestFrom1To2InvalidBid, self).setUp()
#         migrate_data(self.app.app.registry)
#         set_db_schema_version(self.db, 0)
#         auction = self.db.get(self.auction_id)
#         auction['bids'][0]['value']['amount'] = auction['value']['amount']
#         self.db.save(auction)
#
#     test_migrate_one_pending_bid = snitch(migrate_one_pending_bid)
#     test_migrate_one_active_bid = snitch(migrate_one_active_bid)
#     test_migrate_unsuccessful_pending_bid = snitch(migrate_unsuccessful_pending_bid)
#     test_migrate_unsuccessful_active_bid = snitch(migrate_unsuccessful_active_bid)
#
#
# @unittest.skipIf(AWARDING_OF_PROCUREMENT_METHOD_TYPE['dgfOtherAssets'] != 'awarding_2_0', "Awarding 3.0 used")
# class MigrateTestFrom1To2WithTwoBids(BaseAuctionWebTest):
#     initial_status = 'active.qualification'
#     initial_bids = test_bids
#
#     def setUp(self):
#         super(MigrateTestFrom1To2WithTwoBids, self).setUp()
#         migrate_data(self.app.app.registry)
#         set_db_schema_version(self.db, 0)
#
#     test_migrate_pending_to_unsuccesful = snitch(migrate_pending_to_unsuccesful)
#     test_migrate_pending_to_complete = snitch(migrate_pending_to_complete)
#     test_migrate_active_to_unsuccessful = snitch(migrate_active_to_unsuccessful)
#     test_migrate_active_to_complete = snitch(migrate_active_to_complete)
#     test_migrate_cancelled_pending_to_complete = snitch(migrate_cancelled_pending_to_complete)
#     test_migrate_unsuccessful_pending_to_complete = snitch(migrate_unsuccessful_pending_to_complete)
#     test_migrate_unsuccessful_active_to_complete = snitch(migrate_unsuccessful_active_to_complete)
#     test_migrate_cancelled_unsuccessful_pending = snitch(migrate_cancelled_unsuccessful_pending)
#     test_migrate_cancelled_unsuccessful_cancelled_pending_to_unsuccessful = snitch(migrate_cancelled_unsuccessful_cancelled_pending_to_unsuccessful)
#     test_migrate_cancelled_unsuccessful_cancelled_active_to_unsuccessful = snitch(migrate_cancelled_unsuccessful_cancelled_active_to_unsuccessful)
#
#
# @unittest.skipIf(AWARDING_OF_PROCUREMENT_METHOD_TYPE['dgfOtherAssets'] != 'awarding_2_0', "Awarding 3.0 used")
# class MigrateTestFrom1To2WithThreeBids(BaseAuctionWebTest):
#     initial_status = 'active.qualification'
#     initial_bids = test_bids
#
#     def setUp(self):
#         super(MigrateTestFrom1To2WithThreeBids, self).setUp()
#         migrate_data(self.app.app.registry)
#         set_db_schema_version(self.db, 0)
#         auction = self.db.get(self.auction_id)
#         auction['bids'].append(deepcopy(auction['bids'][0]))
#         auction['bids'][-1]['id'] = uuid4().hex
#         self.db.save(auction)
#
#     test_migrate_unsuccessful_unsuccessful_pending = snitch(migrate_unsuccessful_unsuccessful_pending)
#     test_migrate_unsuccessful_unsuccessful_active = snitch(migrate_unsuccessful_unsuccessful_active)
#
#
# @unittest.skipIf(AWARDING_OF_PROCUREMENT_METHOD_TYPE['dgfOtherAssets'] != 'awarding_2_0', "Awarding 3.0 used")
# class MigrateTestFrom1To2SuspendedAuction(BaseAuctionWebTest):
#     initial_status = 'active.qualification'
#     initial_bids = test_bids
#
#     def setUp(self):
#         super(MigrateTestFrom1To2SuspendedAuction, self).setUp()
#         migrate_data(self.app.app.registry)
#         set_db_schema_version(self.db, 0)
#         auction = self.db.get(self.auction_id)
#         auction['suspended'] = True
#         self.db.save(auction)
#
#     test_migrate_pending = snitch(migrate_pending)
#     test_migrate_active = snitch(migrate_active)
#
#
# @unittest.skipIf(AWARDING_OF_PROCUREMENT_METHOD_TYPE['dgfOtherAssets'] != 'awarding_2_0', "Awarding 3.0 used")
# class MigrateTestFrom1To2SuspendedAuctionWithInvalidBids(BaseAuctionWebTest):
#     initial_status = 'active.qualification'
#     initial_bids = test_bids
#
#     def setUp(self):
#         super(MigrateTestFrom1To2SuspendedAuctionWithInvalidBids, self).setUp()
#         migrate_data(self.app.app.registry)
#         set_db_schema_version(self.db, 0)
#         auction = self.db.get(self.auction_id)
#         auction['suspended'] = True
#         for bid in auction['bids']:
#             bid['value']['amount'] = auction['value']['amount']
#         self.db.save(auction)
#
#     test_migrate_one_pending_suspend_bids = snitch(migrate_one_pending_suspend_bids)
#     test_migrate_one_active_suspend_bids = snitch(migrate_one_active_suspend_bids)
#     test_migrate_unsuccessful_pending_suspend_bids = snitch(migrate_unsuccessful_pending_suspend_bids)
#     test_migrate_unsuccessful_active_suspend_bids = snitch(migrate_unsuccessful_active_suspend_bids)
#
#
# @unittest.skipIf(AWARDING_OF_PROCUREMENT_METHOD_TYPE['dgfOtherAssets'] != 'awarding_2_0', "Awarding 3.0 used")
# class MigrateTestFrom1To2SuspendedAuctionWithInvalidBid(BaseAuctionWebTest):
#     initial_status = 'active.qualification'
#     initial_bids = test_bids
#
#     def setUp(self):
#         super(MigrateTestFrom1To2SuspendedAuctionWithInvalidBid, self).setUp()
#         migrate_data(self.app.app.registry)
#         set_db_schema_version(self.db, 0)
#         auction = self.db.get(self.auction_id)
#         auction['suspended'] = True
#         auction['bids'][0]['value']['amount'] = auction['value']['amount']
#         self.db.save(auction)
#
#     test_migrate_one_pending_suspend_bid = snitch(migrate_one_pending_suspend_bid)
#     test_migrate_one_active_suspend_bid = snitch(migrate_one_active_suspend_bid)
#     test_migrate_unsuccessful_pending_suspend_bid = snitch(migrate_unsuccessful_pending_suspend_bid)
#     test_migrate_unsuccessful_active_suspend_bid = snitch(migrate_unsuccessful_active_suspend_bid)


class MigrateTestFrom2To3WithTwoBids(BaseAuctionWebTest, MigrateAwardingV2toV3Mixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    @staticmethod
    def migrate_data(registry, destination=None):
        return migrate_data(registry, destination)

    def setUp(self):
        super(MigrateTestFrom2To3WithTwoBids, self).setUp()
        migrate_data(self.app.app.registry)
        set_db_schema_version(self.db, 1)


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(MigrateTest))
    tests.addTest(unittest.makeSuite(MigrateTestFrom1To2InvalidBids))
    tests.addTest(unittest.makeSuite(MigrateTestFrom1To2InvalidBid))
    tests.addTest(unittest.makeSuite(MigrateTestFrom1To2WithTwoBids))
    tests.addTest(unittest.makeSuite(MigrateTestFrom1To2WithThreeBids))
    tests.addTest(unittest.makeSuite(MigrateTestFrom1To2SuspendedAuction))
    tests.addTest(unittest.makeSuite(MigrateTestFrom1To2SuspendedAuctionWithInvalidBids))
    tests.addTest(unittest.makeSuite(MigrateTestFrom1To2SuspendedAuctionWithInvalidBid))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
