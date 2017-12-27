# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.models import get_now

from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.dgf.models import (
    DGFOtherAssets, DGFFinancialAssets, DGF_ID_REQUIRED_FROM
)
from openprocurement.auctions.dgf.tests.base import (
    test_auction_data, test_financial_auction_data, test_organization,
    test_financial_organization, BaseWebTest, BaseAuctionWebTest
)
from openprocurement.auctions.dgf.tests.tender_blanks import (
    # AuctionTest
    simple_add_auction,
    create_role,
    edit_role,
    # AuctionResourceTest
    empty_listing,
    listing,
    listing_changes,
    listing_draft,
    create_auction_invalid,
    required_dgf_id,
    create_auction_auctionPeriod,
    create_auction_generated,
    create_auction_draft,
    create_auction,
    get_auction,
    auction_features_invalid,
    auction_features,
    patch_tender_jsonpatch,
    patch_auction,
    dateModified_auction,
    auction_not_found,
    guarantee,
    auction_Administrator_change,
    # AuctionProcessTest
    invalid_auction_conditions,
    one_valid_bid_auction,
    one_invalid_bid_auction,
    first_bid_auction,
    suspended_auction,
    # FinancialAuctionResourceTest
    create_auction_generated_financial
)


class AuctionTest(BaseWebTest):
    auction = DGFOtherAssets
    initial_data = test_auction_data

    test_simple_add_auction = snitch(simple_add_auction)
    test_create_role = snitch(create_role)
    test_edit_role = snitch(edit_role)


class AuctionResourceTest(BaseWebTest):
    initial_data = test_auction_data
    initial_organization = test_organization

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_auction_invalid = snitch(create_auction_invalid)
    test_required_dgf_id = unittest.skipIf(
        get_now() < DGF_ID_REQUIRED_FROM,
        "Can`t create auction without dgfID only from {}".format(DGF_ID_REQUIRED_FROM),
    )(snitch(required_dgf_id))
    test_create_auction_auctionPeriod = snitch(create_auction_auctionPeriod)
    test_create_auction_generated = snitch(create_auction_generated)
    test_create_auction_draft = snitch(create_auction_draft)
    test_create_auction = snitch(create_auction)
    test_get_auction = snitch(get_auction)
    test_auction_features_invalid = unittest.skip("option not available")(snitch(auction_features_invalid))
    test_auction_features = unittest.skip("option not available")(snitch(auction_features))
    test_patch_tender_jsonpatch = unittest.skip(
        "this test requires fixed version of jsonpatch library")(snitch(patch_tender_jsonpatch))
    test_patch_auction = snitch(patch_auction)
    test_dateModified_auction = snitch(dateModified_auction)
    test_auction_not_found = snitch(auction_not_found)
    test_guarantee = snitch(guarantee)
    test_auction_Administrator_change = snitch(auction_Administrator_change)


class AuctionProcessTest(BaseAuctionWebTest):
    #setUp = BaseWebTest.setUp
    def setUp(self):
        super(AuctionProcessTest.__bases__[0], self).setUp()

    test_invalid_auction_conditions = unittest.skip("option not available")(snitch(invalid_auction_conditions))
    # _test_one_valid_bid_auction = snitch(one_valid_bid_auction)
    # _test_one_invalid_bid_auction = snitch(one_invalid_bid_auction)
    test_first_bid_auction = snitch(first_bid_auction)
    test_suspended_auction = snitch(suspended_auction)


class FinancialAuctionTest(AuctionTest):
    auction = DGFFinancialAssets


class FinancialAuctionResourceTest(BaseWebTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_auction_invalid = snitch(create_auction_invalid)
    test_required_dgf_id = unittest.skipIf(
        get_now() < DGF_ID_REQUIRED_FROM,
        "Can`t create auction without dgfID only from {}".format(DGF_ID_REQUIRED_FROM),
    )(snitch(required_dgf_id))
    test_create_auction_auctionPeriod = snitch(create_auction_auctionPeriod)

    test_create_auction_draft = snitch(create_auction_draft)
    test_create_auction = snitch(create_auction)
    test_get_auction = snitch(get_auction)
    test_auction_features_invalid = unittest.skip("option not available")(snitch(auction_features_invalid))
    test_auction_features = unittest.skip("option not available")(snitch(auction_features))
    test_patch_tender_jsonpatch = unittest.skip(
        "this test requires fixed version of jsonpatch library")(snitch(patch_tender_jsonpatch))
    test_patch_auction = snitch(patch_auction)
    test_dateModified_auction = snitch(dateModified_auction)
    test_auction_not_found = snitch(auction_not_found)
    test_guarantee = snitch(guarantee)
    test_auction_Administrator_change = snitch(auction_Administrator_change)

    test_create_auction_generated_financial = snitch(create_auction_generated_financial)


class FinancialAuctionProcessTest(AuctionProcessTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionProcessTest))
    suite.addTest(unittest.makeSuite(AuctionResourceTest))
    suite.addTest(unittest.makeSuite(AuctionTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionProcessTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
