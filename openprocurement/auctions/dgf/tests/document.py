# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.dgf.tests.base import BaseAuctionWebTest,  test_financial_auction_data
from openprocurement.auctions.dgf.tests.document_blanks import (
    # AuctionDocumentResourceTest
    not_found,
    create_auction_document,
    put_auction_document,
    patch_auction_document,
    # AuctionDocumentWithDSResourceTest
    create_auction_document_json_invalid,
    create_auction_document_json,
    put_auction_document_json,
    put_auction_document_pas,
    create_auction_offline_document,
    put_auction_offline_document,
    # FinancialAuctionDocumentWithDSResourceTest
    create_auction_document_vdr,
    put_auction_document_vdr
)


class AuctionDocumentResourceTest(BaseAuctionWebTest):
    docservice = False

    test_not_found = snitch(not_found)
    test_create_auction_document = snitch(create_auction_document)
    test_put_auction_document = snitch(put_auction_document)
    test_patch_auction_document = snitch(patch_auction_document)


class AuctionDocumentWithDSResourceTest(BaseAuctionWebTest):
    docservice = True

    test_not_found = snitch(not_found)
    test_create_auction_document = snitch(create_auction_document)
    test_put_auction_document = snitch(put_auction_document)
    test_patch_auction_document = snitch(patch_auction_document)

    test_create_auction_document_json_invalid = snitch(create_auction_document_json_invalid)
    test_create_auction_document_json = snitch(create_auction_document_json)
    test_put_auction_document_json = snitch(put_auction_document_json)
    test_put_auction_document_pas = snitch(put_auction_document_pas)
    test_create_auction_offline_document = snitch(create_auction_offline_document)
    test_put_auction_offline_document = snitch(put_auction_offline_document)


class FinancialAuctionDocumentResourceTest(BaseAuctionWebTest):
    initial_data = test_financial_auction_data
    docservice = False

    test_not_found = snitch(not_found)
    test_create_auction_document = snitch(create_auction_document)
    test_put_auction_document = snitch(put_auction_document)
    test_patch_auction_document = snitch(patch_auction_document)


class FinancialAuctionDocumentWithDSResourceTest(BaseAuctionWebTest):
    initial_data = test_financial_auction_data
    docservice = True

    test_not_found = snitch(not_found)
    test_create_auction_document = snitch(create_auction_document)
    test_put_auction_document = snitch(put_auction_document)
    test_patch_auction_document = snitch(patch_auction_document)

    test_create_auction_document_json_invalid = snitch(create_auction_document_json_invalid)
    test_create_auction_document_json = snitch(create_auction_document_json)
    test_put_auction_document_json = snitch(put_auction_document_json)
    test_put_auction_document_pas = snitch(put_auction_document_pas)
    test_create_auction_offline_document = snitch(create_auction_offline_document)
    test_put_auction_offline_document = snitch(put_auction_offline_document)

    test_create_auction_document_vdr = snitch(create_auction_document_vdr)
    test_put_auction_document_vdr = snitch(put_auction_document_vdr)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionDocumentResourceTest))
    suite.addTest(unittest.makeSuite(AuctionDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionDocumentWithDSResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
