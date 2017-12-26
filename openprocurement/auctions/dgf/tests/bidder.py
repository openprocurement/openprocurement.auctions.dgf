# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest, test_features_auction_data,
    test_financial_organization, test_financial_auction_data
)
from openprocurement.auctions.dgf.tests.bidder_blanks import (
    # AuctionBidderResourceTest
    create_auction_bidder_invalid,
    create_auction_bidder,
    patch_auction_bidder,
    get_auction_bidder,
    delete_auction_bidder,
    get_auction_auctioners,
    bid_Administrator_change,
    # AuctionBidderFeaturesResourceTest
    features_bidder,
    features_bidder_invalid,
    # AuctionBidderDocumentResourceTest
    not_found,
    create_auction_bidder_document,
    put_auction_bidder_document,
    patch_auction_bidder_document,
    create_auction_bidder_document_nopending,
    # AuctionBidderDocumentWithDSResourceTest
    create_auction_bidder_document_json,
    put_auction_bidder_document_json,
    # FinancialAuctionBidderResourceTest
    create_auction_bidder_invalid_additional_classification
)


class AuctionBidderResourceTest(BaseAuctionWebTest):
    initial_status = 'active.tendering'

    test_create_auction_bidder_invalid = snitch(create_auction_bidder_invalid)
    test_create_auction_bidder = snitch(create_auction_bidder)
    test_patch_auction_bidder = snitch(patch_auction_bidder)
    test_get_auction_bidder = snitch(get_auction_bidder)
    test_delete_auction_bidder = snitch(delete_auction_bidder)
    test_get_auction_auctioners = snitch(get_auction_auctioners)
    test_bid_Administrator_change = snitch(bid_Administrator_change)


@unittest.skip("option not available")
class AuctionBidderFeaturesResourceTest(BaseAuctionWebTest):
    initial_data = test_features_auction_data
    initial_status = 'active.tendering'

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class AuctionBidderDocumentResourceTest(BaseAuctionWebTest):
    initial_status = 'active.tendering'

    def setUp(self):
        super(AuctionBidderDocumentResourceTest, self).setUp()
        # Create bid
        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True}})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']

    test_not_found = snitch(not_found)
    test_create_auction_bidder_document = snitch(create_auction_bidder_document)
    test_put_auction_bidder_document = snitch(put_auction_bidder_document)
    test_patch_auction_bidder_document = snitch(patch_auction_bidder_document)
    test_create_auction_bidder_document_nopending = snitch(create_auction_bidder_document_nopending)


class AuctionBidderDocumentWithDSResourceTest(BaseAuctionWebTest):
    initial_status = 'active.tendering'
    docservice = True

    def setUp(self):
        super(AuctionBidderDocumentWithDSResourceTest, self).setUp()
        # Create bid
        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True}})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']

    test_not_found = snitch(not_found)
    test_create_auction_bidder_document = snitch(create_auction_bidder_document)
    test_put_auction_bidder_document = snitch(put_auction_bidder_document)
    test_patch_auction_bidder_document = snitch(patch_auction_bidder_document)
    test_create_auction_bidder_document_nopending = snitch(create_auction_bidder_document_nopending)

    test_create_auction_bidder_document_json = snitch(create_auction_bidder_document_json)
    test_put_auction_bidder_document_json = snitch(put_auction_bidder_document_json)


class FinancialAuctionBidderResourceTest(BaseAuctionWebTest):
    initial_status = 'active.tendering'
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization

    test_create_auction_bidder_invalid = snitch(create_auction_bidder_invalid)
    test_create_auction_bidder = snitch(create_auction_bidder)
    test_patch_auction_bidder = snitch(patch_auction_bidder)
    test_get_auction_bidder = snitch(get_auction_bidder)
    test_delete_auction_bidder = snitch(delete_auction_bidder)
    test_get_auction_auctioners = snitch(get_auction_auctioners)
    test_bid_Administrator_change = snitch(bid_Administrator_change)

    test_create_auction_bidder_invalid_additional_classification = snitch(create_auction_bidder_invalid_additional_classification)


@unittest.skip("option not available")
class FinancialAuctionBidderFeaturesResourceTest(AuctionBidderFeaturesResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionBidderDocumentWithDSResourceTest(AuctionBidderDocumentWithDSResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionDocumentBidderResourceTest(AuctionBidderDocumentResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionBidderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(AuctionBidderDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(AuctionBidderFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(AuctionBidderResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionDocumentBidderResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionBidderDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionBidderFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionBidderResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
