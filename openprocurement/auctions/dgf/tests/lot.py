# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.lot import AuctionLotResourceTestMixin, AuctionLotProcessTestMixin
from openprocurement.auctions.core.tests.blanks.lot_blanks import (
    # AuctionLotFeatureResourceTest
    auction_value,
    auction_features_invalid,
    # AuctionLotBidderResourceTest
    create_auction_bidder_invalid,
    patch_auction_bidder,
    # AuctionLotFeatureBidderResourceTest
    create_auction_bidder_invalid_feature,
    create_auction_bidder_feature
)

from openprocurement.auctions.dgf.tests.base import (
    BaseWebTest, BaseAuctionWebTest, test_lots, test_auction_data,
    test_financial_auction_data, test_financial_organization
)
from openprocurement.auctions.dgf.tests.blanks.lot_blanks import (
    # AuctionLotResourceTest
    patch_auction_currency
)


@unittest.skip("option not available")
class AuctionLotResourceTest(BaseAuctionWebTest, AuctionLotResourceTestMixin):
    test_lots = test_lots
    test_auction_data = test_auction_data

    test_patch_auction_currency = snitch(patch_auction_currency)


@unittest.skip("option not available")
class AuctionLotFeatureResourceTest(BaseAuctionWebTest):
    initial_lots = 2 * test_lots
    test_auction_data = test_auction_data

    test_auction_value = snitch(auction_value)
    test_auction_features_invalid = snitch(auction_features_invalid)


@unittest.skip("option not available")
class AuctionLotBidderResourceTest(BaseAuctionWebTest):

    initial_status = 'active.tendering'
    initial_lots = test_lots

    test_create_auction_bidder_invalid = snitch(create_auction_bidder_invalid)
    test_patch_auction_bidder = snitch(patch_auction_bidder)


@unittest.skip("option not available")
class AuctionLotFeatureBidderResourceTest(BaseAuctionWebTest):
    initial_lots = test_lots

    def setUp(self):
        super(AuctionLotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]['id']
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {"data": {
            "items": [
                {
                    'relatedLot': self.lot_id,
                    'id': '1'
                }
            ],
            "features": [
                {
                    "code": "code_item",
                    "featureOf": "item",
                    "relatedItem": "1",
                    "title": u"item feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_lot",
                    "featureOf": "lot",
                    "relatedItem": self.lot_id,
                    "title": u"lot feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_tenderer",
                    "featureOf": "tenderer",
                    "title": u"tenderer feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                }
            ]
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['items'][0]['relatedLot'], self.lot_id)
        self.set_status('active.tendering')

    test_create_auction_bidder_invalid_feature = snitch(create_auction_bidder_invalid_feature)
    test_create_auction_bidder_feature = snitch(create_auction_bidder_feature)


@unittest.skip("option not available")
class AuctionLotProcessTest(BaseAuctionWebTest, AuctionLotProcessTestMixin):
    setUp = BaseWebTest.setUp
    test_lots = test_lots
    test_auction_data = test_auction_data


@unittest.skip("option not available")
class FinancialAuctionLotResourceTest(AuctionLotResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotFeatureResourceTest(AuctionLotFeatureResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotBidderResourceTest(AuctionLotBidderResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotFeatureBidderResourceTest(AuctionLotFeatureBidderResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotProcessTest(AuctionLotProcessTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionLotResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotBidderResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotProcessTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotBidderResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotProcessTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
