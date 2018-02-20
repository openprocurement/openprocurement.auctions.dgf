# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.cancellation import (
    AuctionCancellationResourceTestMixin,
    AuctionCancellationDocumentResourceTestMixin,
    AuctionLotCancellationResourceTestMixin,
    AuctionLotsCancellationResourceTestMixin
)
from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest,
    test_lots, test_bids,
    test_financial_auction_data,
    test_financial_bids
)


class AuctionCancellationResourceTest(BaseAuctionWebTest,
                                      AuctionCancellationResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_bids

  
@unittest.skip("option not available")
class AuctionLotCancellationResourceTest(BaseAuctionWebTest,
                                         AuctionLotCancellationResourceTestMixin):
    initial_status = 'active.tendering'
    initial_lots = test_lots
    initial_bids = test_bids


@unittest.skip("option not available")
class AuctionLotsCancellationResourceTest(BaseAuctionWebTest,
                                          AuctionLotsCancellationResourceTestMixin):
    initial_status = 'active.tendering'
    initial_lots = 2 * test_lots
    initial_bids = test_bids


class AuctionCancellationDocumentResourceTest(BaseAuctionWebTest,
                                              AuctionCancellationDocumentResourceTestMixin):

    def setUp(self):
        super(AuctionCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/auctions/{}/cancellations'.format(
            self.auction_id), {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']


class FinancialAuctionCancellationResourceTest(AuctionCancellationResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data


@unittest.skip("option not available")
class FinancialAuctionLotsCancellationResourceTest(AuctionLotsCancellationResourceTest):
    initial_data = test_financial_auction_data


class FinancialAuctionCancellationDocumentResourceTest(AuctionCancellationDocumentResourceTest):
    initial_data = test_financial_auction_data


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(AuctionCancellationResourceTest))
    tests.addTest(unittest.makeSuite(AuctionLotCancellationResourceTest))
    tests.addTest(unittest.makeSuite(AuctionLotsCancellationResourceTest))
    tests.addTest(unittest.makeSuite(AuctionCancellationDocumentResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuctionCancellationResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuctionLotsCancellationResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuctionCancellationDocumentResourceTest))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
