# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest,
    test_bids,
)
from openprocurement.auctions.core.tests.items import (
    DgfItemsResourceTestMixin,
)


class DgfItemsResourceTest(BaseAuctionWebTest, DgfItemsResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_bids


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DgfItemsResourceTest))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
