# -*- coding: utf-8 -*-
import unittest

from datetime import timedelta

from openprocurement.auctions.core.utils import get_now

from openprocurement.auctions.core.tests.award import (
    AuctionLotAwardResourceTestMixin,
    Auction2LotAwardResourceTestMixin,
    AuctionAwardDocumentResourceTestMixin,
    AuctionLotAwardComplaintResourceTestMixin,
    Auction2LotAwardComplaintResourceTestMixin,
    AuctionAwardComplaintDocumentResourceTestMixin,
    Auction2LotAwardComplaintDocumentResourceTestMixin,
    Auction2LotAwardDocumentResourceTestMixin
)
from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.award_blanks import (
    get_auction_award_complaint,
    get_auction_award_complaints
)
from openprocurement.auctions.core.plugins.awarding.v3.tests.award import (
    AuctionAwardProcessTestMixin,
    CreateAuctionAwardTestMixin
)

from openprocurement.auctions.dgf.tests.base import (
    BaseAuctionWebTest, test_bids,
    test_lots, test_financial_auction_data,
    test_financial_bids, test_financial_organization,
)


class CreateAuctionAwardTest(BaseAuctionWebTest, CreateAuctionAwardTestMixin):
    # initial_data = auction_data
    initial_status = 'active.auction'
    initial_bids = test_bids


class AuctionAwardProcessTest(BaseAuctionWebTest, AuctionAwardProcessTestMixin):
    # initial_data = auction_data
    initial_status = 'active.auction'
    initial_bids = test_bids
    docservice = True

    def setUp(self):
        super(AuctionAwardProcessTest, self).setUp()

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
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        self.assertEqual('active.qualification', auction["status"])
        self.first_award = auction['awards'][0]
        self.second_award = auction['awards'][1]
        self.first_award_id = self.first_award['id']
        self.second_award_id = self.second_award['id']
        self.app.authorization = authorization

    def upload_auction_protocol(self, award):
        award_id = award['id']
        bid_token = self.initial_bids_tokens[award['bid_id']]
        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, award_id, bid_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('auction_protocol.pdf', response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.patch_json(
            '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award_id, doc_id, bid_token),
            {"data": {
                "description": "auction protocol",
                "documentType": 'auctionProtocol'
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn("documentType", response.json["data"])
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('auction_protocol.pdf', response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.patch_json(
            '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award_id, doc_id,
                                                                      self.auction_token),
            {"data": {
                "description": "auction protocol",
                "documentType": 'auctionProtocol'
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn("documentType", response.json["data"])
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

        response = self.app.get('/auctions/{}/awards/{}/documents'.format(self.auction_id, award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual('auctionProtocol', response.json["data"][0]["documentType"])
        self.assertEqual('auction_protocol.pdf', response.json["data"][0]["title"])
        self.assertEqual('bid_owner', response.json["data"][0]["author"])
        self.assertEqual('auctionProtocol', response.json["data"][1]["documentType"])
        self.assertEqual('auction_owner', response.json["data"][1]["author"])


@unittest.skip("option not available")
class AuctionLotAwardResourceTest(BaseAuctionWebTest, AuctionLotAwardResourceTestMixin):
    initial_status = 'active.qualification'
    initial_lots = test_lots
    initial_bids = test_bids


@unittest.skip("option not available")
class Auction2LotAwardResourceTest(BaseAuctionWebTest, Auction2LotAwardResourceTestMixin):
    initial_status = 'active.qualification'
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    # test_create_auction_award_2_lots = snitch(create_auction_award_2_lots)
    # test_patch_auction_award_2_lots = snitch(patch_auction_award_2_lots)


@unittest.skip("option not available")
class AuctionLotAwardComplaintResourceTest(BaseAuctionWebTest,
                                           AuctionLotAwardComplaintResourceTestMixin):
    # initial_data = auction_data
    initial_status = 'active.qualification'
    initial_lots = test_lots
    initial_bids = test_bids

    def setUp(self):
        super(AuctionLotAwardComplaintResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {
            'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': bid['id'],
                     'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']


@unittest.skip("option not available")
class Auction2LotAwardComplaintResourceTest(BaseAuctionWebTest,
                                            Auction2LotAwardComplaintResourceTestMixin):
    initial_status = 'active.qualification'
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    test_get_auction_award_complaint = snitch(get_auction_award_complaint)
    test_get_auction_award_complaints = snitch(get_auction_award_complaints)


@unittest.skip("option not available")
class AuctionAwardComplaintDocumentResourceTest(BaseAuctionWebTest,
                                                AuctionAwardComplaintDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(AuctionAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending',
                                        'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        # Create complaint for award
        response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
            self.auction_id, self.award_id), {
            'data': {'title': 'complaint title', 'description': 'complaint description',
                     'author': self.initial_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']


@unittest.skip("option not available")
class Auction2LotAwardComplaintDocumentResourceTest(BaseAuctionWebTest,
                                                    Auction2LotAwardComplaintDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Auction2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {
            'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': bid['id'],
                     'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        # Create complaint for award
        response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
            self.auction_id, self.award_id), {
            'data': {'title': 'complaint title', 'description': 'complaint description',
                     'author': self.initial_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']


class AuctionAwardDocumentResourceTest(BaseAuctionWebTest,
                                       AuctionAwardDocumentResourceTestMixin):
    initial_status = 'active.auction'
    initial_bids = test_bids

    def setUp(self):
        super(AuctionAwardDocumentResourceTest, self).setUp()
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
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        self.assertEqual('active.qualification', auction["status"])
        self.first_award = auction['awards'][0]
        self.second_award = auction['awards'][1]
        self.first_award_id = self.first_award['id']
        self.second_award_id = self.second_award['id']
        self.app.authorization = authorization

        # test_not_found_document = snitch(not_found_document)
        # test_create_auction_award_document = snitch(create_auction_award_document)
        # test_put_auction_award_document = snitch(put_auction_award_document)
        # test_patch_auction_award_document = snitch(patch_auction_award_document)


@unittest.skip("option not available")
class Auction2LotAwardDocumentResourceTest(BaseAuctionWebTest,
                                           Auction2LotAwardDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Auction2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {
            'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': bid['id'],
                     'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']


class CreateFinancialAuctionAwardTest(CreateAuctionAwardTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionAwardProcessTest(AuctionAwardProcessTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotAwardResourceTest(AuctionLotAwardResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuction2LotAwardResourceTest(Auction2LotAwardResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotAwardComplaintResourceTest(AuctionLotAwardComplaintResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data


@unittest.skip("option not available")
class FinancialAuction2LotAwardComplaintResourceTest(Auction2LotAwardComplaintResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionAwardComplaintDocumentResourceTest(AuctionAwardComplaintDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuction2LotAwardComplaintDocumentResourceTest(Auction2LotAwardComplaintDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionAwardDocumentResourceTest(AuctionAwardDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuction2LotAwardDocumentResourceTest(Auction2LotAwardDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(CreateAuctionAwardTest))
    tests.addTest(unittest.makeSuite(AuctionAwardProcessTest))
    tests.addTest(unittest.makeSuite(AuctionLotAwardResourceTest))
    tests.addTest(unittest.makeSuite(Auction2LotAwardResourceTest))
    tests.addTest(unittest.makeSuite(AuctionLotAwardComplaintResourceTest))
    tests.addTest(unittest.makeSuite(Auction2LotAwardComplaintResourceTest))
    tests.addTest(unittest.makeSuite(AuctionAwardComplaintDocumentResourceTest))
    tests.addTest(unittest.makeSuite(Auction2LotAwardComplaintDocumentResourceTest))
    tests.addTest(unittest.makeSuite(AuctionAwardDocumentResourceTest))
    tests.addTest(unittest.makeSuite(Auction2LotAwardDocumentResourceTest))
    tests.addTest(unittest.makeSuite(CreateFinancialAuctionAwardTest))
    tests.addTest(unittest.makeSuite(FinancialAuctionAwardProcessTest))
    tests.addTest(unittest.makeSuite(FinancialAuctionLotAwardResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuction2LotAwardResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuctionLotAwardComplaintResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuction2LotAwardComplaintResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuctionAwardComplaintDocumentResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuction2LotAwardComplaintDocumentResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuctionAwardDocumentResourceTest))
    tests.addTest(unittest.makeSuite(FinancialAuction2LotAwardDocumentResourceTest))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')