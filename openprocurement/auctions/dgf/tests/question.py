# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.question import AuctionQuestionResourceTestMixin
from openprocurement.auctions.core.tests.blanks.question_blanks import (
    # AuctionLotQuestionResourceTest
    create_auction_question_lot,
    patch_auction_question_lot
)

from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest, test_lots, test_financial_auction_data, test_financial_organization
)


class AuctionQuestionResourceTest(BaseAuctionWebTest, AuctionQuestionResourceTestMixin):
    pass


@unittest.skip("option not available")
class AuctionLotQuestionResourceTest(BaseAuctionWebTest):
    initial_lots = 2 * test_lots

    test_create_auction_question_lot = snitch(create_auction_question_lot)
    test_patch_auction_question_lot = snitch(patch_auction_question_lot)


class FinancialAuctionQuestionResourceTest(AuctionQuestionResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotQuestionResourceTest(AuctionLotQuestionResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionQuestionResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotQuestionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionQuestionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
