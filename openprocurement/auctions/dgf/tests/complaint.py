# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest, test_lots,
    test_financial_auction_data, test_financial_organization
)
from openprocurement.auctions.dgf.tests.blanks.complaint_blanks import (
    # AuctionComplaintResourceTest
    create_auction_complaint_invalid,
    create_auction_complaint,
    patch_auction_complaint,
    review_auction_complaint,
    get_auction_complaint,
    get_auction_complaints,
    # AuctionLotAwardComplaintResourceTest
    create_auction_complaint_lot,
    # AuctionComplaintDocumentResourceTest
    not_found,
    create_auction_complaint_document,
    put_auction_complaint_document,
    patch_auction_complaint_document
)


class AuctionComplaintResourceTest(BaseAuctionWebTest):

    test_create_auction_complaint_invalid = snitch(create_auction_complaint_invalid)
    test_create_auction_complaint = snitch(create_auction_complaint)
    test_patch_auction_complaint = snitch(patch_auction_complaint)
    test_review_auction_complaint = snitch(review_auction_complaint)
    test_get_auction_complaint = snitch(get_auction_complaint)
    test_get_auction_complaints = snitch(get_auction_complaints)


@unittest.skip("option not available")
class AuctionLotAwardComplaintResourceTest(BaseAuctionWebTest):
    initial_lots = test_lots

    test_create_auction_complaint_lot = snitch(create_auction_complaint_lot)


class AuctionComplaintDocumentResourceTest(BaseAuctionWebTest):

    def setUp(self):
        super(AuctionComplaintDocumentResourceTest, self).setUp()
        # Create complaint
        response = self.app.post_json('/auctions/{}/complaints'.format(
            self.auction_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.initial_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_not_found = snitch(not_found)
    test_create_auction_complaint_document = snitch(create_auction_complaint_document)
    test_put_auction_complaint_document = snitch(put_auction_complaint_document)
    test_patch_auction_complaint_document = snitch(patch_auction_complaint_document)


class FinancialAuctionComplaintResourceTest(BaseAuctionWebTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotAwardComplaint(BaseAuctionWebTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionComplaintDocumentResourceTest(BaseAuctionWebTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(AuctionComplaintResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
