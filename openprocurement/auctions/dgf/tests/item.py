# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest,
    test_financial_auction_data,
)
from openprocurement.auctions.core.tests.items import (
    DgfItemsResourceTestMixin,
)


class DgfOtherItemsResourceTest(BaseAuctionWebTest, DgfItemsResourceTestMixin):
    initial_status = 'active.tendering'


class DgfFinancialItemsResourceTest(BaseAuctionWebTest, DgfItemsResourceTestMixin):
    initial_status = 'active.tendering'
    initial_data = test_financial_auction_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DgfOtherItemsResourceTest))
    suite.addTest(unittest.makeSuite(DgfFinancialItemsResourceTest))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
