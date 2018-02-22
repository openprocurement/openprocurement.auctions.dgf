# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.dgf.models import DGF_PLATFORM_LEGAL_DETAILS_FROM

from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest,  test_financial_auction_data
)
from openprocurement.auctions.core.tests.document import (
    AuctionDocumentResourceTestMixin,
    AuctionDocumentWithDSResourceTestMixin
)
from openprocurement.auctions.core.tests.blanks.document_blanks import (
    # FinancialAuctionDocumentWithDSResourceTest
    create_auction_document_vdr,
    put_auction_document_vdr
)


class AuctionDocumentResourceTest(BaseAuctionWebTest, AuctionDocumentResourceTestMixin):
    docservice = False
    dgf_platform_legal_details_from = DGF_PLATFORM_LEGAL_DETAILS_FROM


class AuctionDocumentWithDSResourceTest(BaseAuctionWebTest, AuctionDocumentResourceTestMixin, AuctionDocumentWithDSResourceTestMixin):
    docservice = True
    dgf_platform_legal_details_from = DGF_PLATFORM_LEGAL_DETAILS_FROM

    # TODO this TestCase didn't contain "test_create_auction_document_pas"


class FinancialAuctionDocumentResourceTest(BaseAuctionWebTest, AuctionDocumentResourceTestMixin):
    initial_data = test_financial_auction_data
    docservice = False
    dgf_platform_legal_details_from = DGF_PLATFORM_LEGAL_DETAILS_FROM


class FinancialAuctionDocumentWithDSResourceTest(BaseAuctionWebTest, AuctionDocumentResourceTestMixin, AuctionDocumentWithDSResourceTestMixin):
    initial_data = test_financial_auction_data
    docservice = True
    dgf_platform_legal_details_from = DGF_PLATFORM_LEGAL_DETAILS_FROM

    # TODO this TestCase didn't contain "test_create_auction_document_pas"

    test_create_auction_document_vdr = snitch(create_auction_document_vdr)
    test_put_auction_document_vdr = snitch(put_auction_document_vdr)


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(AuctionDocumentResourceTest))
    tests.addTest(unittest.makeSuite(AuctionDocumentWithDSResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuctionDocumentResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuctionDocumentWithDSResourceTest))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
