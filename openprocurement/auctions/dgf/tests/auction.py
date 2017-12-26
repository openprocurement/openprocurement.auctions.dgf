# -*- coding: utf-8 -*-
import unittest

from copy import deepcopy

from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest, test_bids, test_lots, test_organization, test_features_auction_data,
    test_financial_auction_data, test_financial_bids, test_financial_organization, test_auction_data
)
from openprocurement.auctions.dgf.tests.auction_blanks import (
    # AuctionAuctionResourceTest
    get_auction_auction_not_found,
    get_auction_auction,
    post_auction_auction,
    patch_auction_auction,
    post_auction_auction_document,
    # AuctionBidInvalidationAuctionResourceTest
    post_auction_all_invalid_bids,
    post_auction_one_invalid_bid,
    post_auction_one_valid_bid,
    # AuctionSameValueAuctionResourceTest
    post_auction_auction_not_changed,
    post_auction_auction_reversed,
    # AuctionLotAuctionResourceTest
    get_auction_auction_lot,
    post_auction_auction_lot,
    patch_auction_auction_lot,
    post_auction_auction_document_lot,
    # AuctionMultipleLotAuctionResourceTest
    get_auction_auction_2_lots,
    post_auction_auction_2_lots,
    patch_auction_auction_2_lots,
    post_auction_auction_document_2_lots,
    # AuctionFeaturesAuctionResourceTest
    get_auction_auction_features
)


class AuctionAuctionResourceTest(BaseAuctionWebTest):
    # initial_data = auction_data
    initial_status = 'active.tendering'
    initial_bids = test_bids

    test_get_auction_auction_not_found = snitch(get_auction_auction_not_found)
    test_get_auction_auction = snitch(get_auction_auction)
    test_post_auction_auction = snitch(post_auction_auction)
    test_patch_auction_auction = snitch(patch_auction_auction)
    test_post_auction_auction_document = snitch(post_auction_auction_document)


class AuctionBidInvalidationAuctionResourceTest(BaseAuctionWebTest):
    initial_data = test_auction_data
    initial_status = 'active.auction'
    initial_bids = [
        {
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": (initial_data['value']['amount'] + initial_data['minimalStep']['amount']/2),
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'qualified': True
        }
        for i in range(3)
    ]

    test_post_auction_all_invalid_bids = snitch(post_auction_all_invalid_bids)
    test_post_auction_one_invalid_bid = snitch(post_auction_one_invalid_bid)
    test_post_auction_one_valid_bid = snitch(post_auction_one_valid_bid)


class AuctionSameValueAuctionResourceTest(BaseAuctionWebTest):
    initial_status = 'active.auction'
    initial_bids = [
        {
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'qualified': True
        }
        for i in range(3)
    ]

    test_post_auction_auction_not_changed = snitch(post_auction_auction_not_changed)
    test_post_auction_auction_reversed = snitch(post_auction_auction_reversed)


@unittest.skip("option not available")
class AuctionLotAuctionResourceTest(BaseAuctionWebTest):
    initial_lots = test_lots

    test_get_auction_auction_not_found = snitch(get_auction_auction_not_found)
    test_get_auction_auction_lot = snitch(get_auction_auction_lot)
    test_post_auction_auction_lot = snitch(post_auction_auction_lot)
    test_patch_auction_auction_lot = snitch(patch_auction_auction_lot)
    test_post_auction_auction_document_lot = snitch(post_auction_auction_document_lot)


@unittest.skip("option not available")
class AuctionMultipleLotAuctionResourceTest(BaseAuctionWebTest):
    initial_lots = 2 * test_lots

    test_get_auction_auction_not_found = snitch(get_auction_auction_not_found)
    test_get_auction_auction_2_lots = snitch(get_auction_auction_2_lots)
    test_post_auction_auction_2_lots = snitch(post_auction_auction_2_lots)
    test_patch_auction_auction_2_lots = snitch(patch_auction_auction_2_lots)
    test_post_auction_auction_document_2_lots = snitch(post_auction_auction_document_2_lots)


@unittest.skip("option not available")
class AuctionFeaturesAuctionResourceTest(BaseAuctionWebTest):
    initial_data = test_features_auction_data
    initial_status = 'active.auction'
    initial_bids = [
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.1,
                }
                for i in test_features_auction_data['features']
            ],
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'qualified': True
        },
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.15,
                }
                for i in test_features_auction_data['features']
            ],
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": 479,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            }
        }
    ]

    test_get_auction_auction_features = snitch(get_auction_auction_features)


class FinancialAuctionAuctionResourceTest(AuctionAuctionResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data


class FinancialAuctionSameValueAuctionResourceTest(AuctionSameValueAuctionResourceTest):
    initial_data = test_financial_auction_data
    initial_bids = [
        {
            "tenderers": [
                test_financial_organization
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'qualified': True,
            'eligible': True
        }
        for i in range(3)
    ]


@unittest.skip("option not available")
class FinancialAuctionLotAuctionResourceTest(AuctionLotAuctionResourceTest):
    initial_data = test_financial_auction_data
    initial_bids = test_financial_bids


@unittest.skip("option not available")
class FinancialAuctionMultipleLotAuctionResourceTest(AuctionMultipleLotAuctionResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data


@unittest.skip("option not available")
class FinancialAuctionFeaturesAuctionResourceTest(AuctionFeaturesAuctionResourceTest):
    initial_data = deepcopy(test_features_auction_data)
    initial_data["procurementMethodType"] = "dgfFinancialAssets"
    initial_bids = [
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.1,
                }
                for i in test_features_auction_data['features']
            ],
            "tenderers": [
                test_financial_organization
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'qualified': True,
            'eligible': True
        },
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.15,
                }
                for i in test_features_auction_data['features']
            ],
            "tenderers": [
                test_financial_organization
            ],
            "value": {
                "amount": 479,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'qualified': True,
            'eligible': True
        }
    ]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionAuctionResourceTest))
    suite.addTest(unittest.makeSuite(AuctionSameValueAuctionResourceTest))
    suite.addTest(unittest.makeSuite(AuctionFeaturesAuctionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionAuctionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionSameValueAuctionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionFeaturesAuctionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
