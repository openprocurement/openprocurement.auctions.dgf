# -*- coding: utf-8 -*-
import unittest
from datetime import timedelta

from openprocurement.api.models import get_now

from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest, test_bids, test_lots, test_financial_auction_data,
    test_financial_bids, test_financial_organization
)
from openprocurement.auctions.core.tests.contract import (
    AuctionContractResourceTestMixin,
    AuctionContractDocumentResourceTestMixin,
    Auction2LotContractDocumentResourceTestMixin
)
from openprocurement.auctions.core.tests.blanks.contract_blanks import (
    # AuctionContractResourceTest
    patch_auction_contract,
    # Auction2LotContractResourceTest
    patch_auction_contract_2_lots,
    patch_signing_period,
    patch_date_paid,
)


class AuctionContractResourceTest(BaseAuctionWebTest, AuctionContractResourceTestMixin):
    #initial_data = auction_data
    initial_status = 'active.auction'
    initial_bids = test_bids

    def setUp(self):
        super(AuctionContractResourceTest, self).setUp()
        # Create award
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('auction', ''))
        now = get_now()
        auction_result = {
            'bids': [
                {
                    "id": b['id'],
                    "date": (now - timedelta(seconds=i)).isoformat(),
                    "value": b['value']
                }
                for i, b in enumerate(self.initial_bids)
            ]
        }

        response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': auction_result})
        self.assertEqual(response.status, '200 OK')
        auction = response.json['data']
        self.app.authorization = authorization
        self.award = auction['awards'][0]
        self.award_id = self.award['id']
        self.award_value = self.award['value']
        self.award_suppliers = self.award['suppliers']

        self.set_status('active.qualification')

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, self.award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']

        response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, doc_id, self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')
        self.assertEqual(response.json["data"]["author"], 'auction_owner')

        self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "pending"}})
        self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "active"}})

    test_patch_auction_contract = snitch(patch_auction_contract)
    test_patch_signing_period = snitch(patch_signing_period)
    test_patch_date_paid = snitch(patch_date_paid)


@unittest.skip("option not available")
class Auction2LotContractResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Auction2LotContractResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/auctions/{}/awards'.format(self.auction_id), {'data': {
            'suppliers': [self.initial_organization],
            'status': 'pending',
            'bid_id': self.initial_bids[0]['id'],
            'lotID': self.initial_lots[0]['id']
        }})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "active"}})

    test_patch_auction_contract_2_lots = snitch(patch_auction_contract_2_lots)


class AuctionContractDocumentResourceTest(BaseAuctionWebTest, AuctionContractDocumentResourceTestMixin):
    #initial_data = auction_data
    initial_status = 'active.auction'
    initial_bids = test_bids

    def setUp(self):
        super(AuctionContractDocumentResourceTest, self).setUp()
        # Create award
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('auction', ''))
        now = get_now()
        auction_result = {
            'bids': [
                {
                    "id": b['id'],
                    "date": (now - timedelta(seconds=i)).isoformat(),
                    "value": b['value']
                }
                for i, b in enumerate(self.initial_bids)
            ]
        }

        response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': auction_result})
        self.assertEqual(response.status, '200 OK')
        auction = response.json['data']
        self.app.authorization = authorization
        self.award = auction['awards'][0]
        self.award_id = self.award['id']
        self.award_value = self.award['value']
        self.award_suppliers = self.award['suppliers']

        self.set_status('active.qualification')

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, self.award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']

        response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, doc_id, self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')
        self.assertEqual(response.json["data"]["author"], 'auction_owner')

        self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "pending"}})
        self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "active"}})
        # Create contract for award
        response = self.app.post_json('/auctions/{}/contracts'.format(self.auction_id), {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}})
        contract = response.json['data']
        self.contract_id = contract['id']


@unittest.skip("option not available")
class Auction2LotContractDocumentResourceTest(BaseAuctionWebTest, Auction2LotContractDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Auction2LotContractDocumentResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/auctions/{}/awards'.format(self.auction_id), {'data': {
            'suppliers': [self.initial_organization],
            'status': 'pending',
            'bid_id': self.initial_bids[0]['id'],
            'lotID': self.initial_lots[0]['id']
        }})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "active"}})
        # Create contract for award
        response = self.app.post_json('/auctions/{}/contracts'.format(self.auction_id), {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}})
        contract = response.json['data']
        self.contract_id = contract['id']


class FinancialAuctionContractResourceTest(AuctionContractResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuction2LotContractResourceTest(Auction2LotContractResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuction2LotContractDocumentResourceTest(Auction2LotContractDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionContractDocumentResourceTest(AuctionContractDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionContractResourceTest))
    suite.addTest(unittest.makeSuite(AuctionContractDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionContractResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionContractDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
