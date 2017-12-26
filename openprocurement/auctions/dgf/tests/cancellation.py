# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest, test_lots, test_bids, test_financial_auction_data, test_financial_bids
)
from openprocurement.auctions.dgf.tests.cancellation_blanks import (
    # AuctionCancellationResourceTest
    create_auction_cancellation_invalid,
    create_auction_cancellation,
    patch_auction_cancellation,
    get_auction_cancellation,
    get_auction_cancellations,
    # AuctionLotCancellationResourceTest
    create_auction_cancellation_lot,
    patch_auction_cancellation_lot,
    # AuctionLotsCancellationResourceTest
    create_auction_cancellation_2_lots,
    patch_auction_cancellation_2_lots,
    # AuctionCancellationDocumentResourceTest
    not_found,
    create_auction_cancellation_document,
    put_auction_cancellation_document,
    patch_auction_cancellation_document
)


class AuctionCancellationResourceTest(BaseAuctionWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids

    test_create_auction_cancellation_invalid = snitch(create_auction_cancellation_invalid)
    test_create_auction_cancellation = snitch(create_auction_cancellation)
    test_patch_auction_cancellation = snitch(patch_auction_cancellation)
    test_get_auction_cancellation = snitch(get_auction_cancellation)
    test_get_auction_cancellations = snitch(get_auction_cancellations)


@unittest.skip("option not available")
class AuctionLotCancellationResourceTest(BaseAuctionWebTest):
    initial_status = 'active.tendering'
    initial_lots = test_lots
    initial_bids = test_bids

    test_create_auction_cancellation_lot = snitch(create_auction_cancellation_lot)
    test_patch_auction_cancellation_lot = snitch(patch_auction_cancellation_lot)


@unittest.skip("option not available")
class AuctionLotsCancellationResourceTest(BaseAuctionWebTest):
    initial_status = 'active.tendering'
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    test_create_auction_cancellation_2_lots = snitch(create_auction_cancellation_2_lots)
    test_patch_auction_cancellation_2_lots = snitch(patch_auction_cancellation_2_lots)


class AuctionCancellationDocumentResourceTest(BaseAuctionWebTest):

    def setUp(self):
        super(AuctionCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/auctions/{}/cancellations'.format(
            self.auction_id), {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']

    test_not_found = snitch(not_found)
    test_create_auction_cancellation_document = snitch(create_auction_cancellation_document)
    test_put_auction_cancellation_document = snitch(put_auction_cancellation_document)
    test_patch_auction_cancellation_document = snitch(patch_auction_cancellation_document)


class FinancialAuctionCancellationResourceTest(AuctionCancellationResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data


@unittest.skip("option not available")
class FinancialAuctionLotsCancellationResourceTest(AuctionLotsCancellationResourceTest):
    initial_data = test_financial_auction_data


class FinancialAuctionCancellationDocumentResourceTest(AuctionCancellationDocumentResourceTest):
    initial_data = test_financial_auction_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotsCancellationResourceTest))
    suite.addTest(unittest.makeSuite(AuctionCancellationResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotsCancellationResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionCancellationResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
