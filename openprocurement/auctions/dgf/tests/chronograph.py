# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timedelta
from openprocurement.api.models import get_now
from openprocurement.auctions.dgf.tests.base import BaseAuctionWebTest, test_lots, test_bids, test_financial_auction_data, test_financial_organization, test_financial_bids


class AuctionSwitchQualificationResourceTest(BaseAuctionWebTest):
    initial_bids = test_bids[:1]

    def test_switch_to_qualification(self):
        response = self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "unsuccessful")
        self.assertNotIn("awards", response.json['data'])


class AuctionSwitchAuctionResourceTest(BaseAuctionWebTest):
    initial_bids = test_bids

    def test_switch_to_auction(self):
        response = self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active.auction")


class AuctionSwitchUnsuccessfulResourceTest(BaseAuctionWebTest):

    def test_switch_to_unsuccessful(self):
        response = self.set_status('active.auction', {'status': self.initial_status})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "unsuccessful")
        if self.initial_lots:
            self.assertEqual(set([i['status'] for i in response.json['data']["lots"]]), set(["unsuccessful"]))


@unittest.skip("option not available")
class AuctionLotSwitchQualificationResourceTest(AuctionSwitchQualificationResourceTest):
    initial_lots = test_lots


@unittest.skip("option not available")
class AuctionLotSwitchAuctionResourceTest(AuctionSwitchAuctionResourceTest):
    initial_lots = test_lots


@unittest.skip("option not available")
class AuctionLotSwitchUnsuccessfulResourceTest(AuctionSwitchUnsuccessfulResourceTest):
    initial_lots = test_lots


class AuctionAuctionPeriodResourceTest(BaseAuctionWebTest):
    initial_bids = test_bids

    def test_set_auction_period(self):
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.tendering')
        if self.initial_lots:
            item = response.json['data']["lots"][0]
        else:
            item = response.json['data']
        self.assertIn('auctionPeriod', item)
        self.assertIn('shouldStartAfter', item['auctionPeriod'])
        self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
        self.assertIn('T00:00:00+', item['auctionPeriod']['shouldStartAfter'])
        self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

        if self.initial_lots:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}]}})
            item = response.json['data']["lots"][0]
        else:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}})
            item = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(item['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

        if self.initial_lots:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"lots": [{"auctionPeriod": {"startDate": None}}]}})
            item = response.json['data']["lots"][0]
        else:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"auctionPeriod": {"startDate": None}}})
            item = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('startDate', item['auctionPeriod'])

    def test_reset_auction_period(self):
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.tendering')
        if self.initial_lots:
            item = response.json['data']["lots"][0]
        else:
            item = response.json['data']
        self.assertIn('auctionPeriod', item)
        self.assertIn('shouldStartAfter', item['auctionPeriod'])
        self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
        self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

        if self.initial_lots:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
            item = response.json['data']["lots"][0]
        else:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
            item = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
        self.assertIn('9999-01-01T00:00:00', item['auctionPeriod']['startDate'])

        self.set_status('active.auction', {'status': 'active.tendering'})
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["status"], 'active.auction')
        item = response.json['data']["lots"][0] if self.initial_lots else response.json['data']
        self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])

        if self.initial_lots:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
            item = response.json['data']["lots"][0]
        else:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
            item = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["status"], 'active.auction')
        self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
        self.assertIn('9999-01-01T00:00:00', item['auctionPeriod']['startDate'])
        self.assertIn('9999-01-01T00:00:00', response.json['data']['next_check'])

        now = get_now().isoformat()
        auction = self.db.get(self.auction_id)
        if self.initial_lots:
            auction['lots'][0]['auctionPeriod']['startDate'] = now
        else:
            auction['auctionPeriod']['startDate'] = now
        self.db.save(auction)

        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["status"], 'active.auction')
        item = response.json['data']["lots"][0] if self.initial_lots else response.json['data']
        self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
        self.assertGreater(response.json['data']['next_check'], item['auctionPeriod']['startDate'])
        self.assertEqual(response.json['data']['next_check'], self.db.get(self.auction_id)['next_check'])

        if self.initial_lots:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"lots": [{"auctionPeriod": {"startDate": response.json['data']['tenderPeriod']['endDate']}}]}})
            item = response.json['data']["lots"][0]
        else:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"auctionPeriod": {"startDate": response.json['data']['tenderPeriod']['endDate']}}})
            item = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["status"], 'active.auction')
        self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
        self.assertNotIn('9999-01-01T00:00:00', item['auctionPeriod']['startDate'])
        self.assertGreater(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

        auction = self.db.get(self.auction_id)
        self.assertGreater(auction['next_check'], response.json['data']['tenderPeriod']['endDate'])
        auction['tenderPeriod']['endDate'] = auction['tenderPeriod']['startDate']
        if self.initial_lots:
            auction['lots'][0]['auctionPeriod']['startDate'] = auction['tenderPeriod']['startDate']
        else:
            auction['auctionPeriod']['startDate'] = auction['tenderPeriod']['startDate']
        self.db.save(auction)

        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        if self.initial_lots:
            item = response.json['data']["lots"][0]
        else:
            item = response.json['data']
        self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
        self.assertNotIn('next_check', response.json['data'])
        self.assertNotIn('next_check', self.db.get(self.auction_id))
        shouldStartAfter = item['auctionPeriod']['shouldStartAfter']

        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        if self.initial_lots:
            item = response.json['data']["lots"][0]
        else:
            item = response.json['data']
        self.assertEqual(item['auctionPeriod']['shouldStartAfter'], shouldStartAfter)
        self.assertNotIn('next_check', response.json['data'])

        if self.initial_lots:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
            item = response.json['data']["lots"][0]
        else:
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
            item = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["status"], 'active.auction')
        self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
        self.assertIn('9999-01-01T00:00:00', item['auctionPeriod']['startDate'])
        self.assertIn('9999-01-01T00:00:00', response.json['data']['next_check'])


class AuctionAwardSwitchResourceTest(BaseAuctionWebTest):
    initial_status = 'active.auction'
    initial_bids = test_bids

    def setUp(self):
        super(AuctionAwardSwitchResourceTest, self).setUp()
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
        self.award = self.first_award = auction['awards'][0]
        self.second_award = auction['awards'][1]
        self.award_id = self.first_award_id = self.first_award['id']
        self.second_award_id = self.second_award['id']
        self.app.authorization = authorization

    def test_switch_verification_to_unsuccessful(self):
        auction = self.db.get(self.auction_id)
        auction['awards'][0]['verificationPeriod']['endDate'] = auction['awards'][0]['verificationPeriod']['startDate']
        self.db.save(auction)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        auction = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(auction['awards'][0]['status'], 'unsuccessful')
        self.assertEqual(auction['awards'][1]['status'], 'pending.verification')
        self.assertEqual(auction['status'], 'active.qualification')
        self.assertNotIn('endDate', auction['awardPeriod'])


    def test_switch_verification_to_payment(self):
        # response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "active"}})
        # self.assertEqual(response.status, '200 OK')
        # self.assertEqual(response.content_type, 'application/json')
        # self.assertEqual(response.json['data']["status"], "active")

        bid_token = self.initial_bids_tokens[self.award['bid_id']]
        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, self.award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, doc_id, self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

        auction = self.db.get(self.auction_id)
        auction['awards'][0]['verificationPeriod']['endDate'] = auction['awards'][0]['verificationPeriod']['startDate']
        self.db.save(auction)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['awards'][0]['status'], 'pending.payment')

    def test_switch_payment_to_unsuccessful(self):
        bid_token = self.initial_bids_tokens[self.award['bid_id']]
        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, self.award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, doc_id, self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

        response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "pending.payment"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "pending.payment")

        auction = self.db.get(self.auction_id)
        auction['awards'][0]['paymentPeriod']['endDate'] = auction['awards'][0]['paymentPeriod']['startDate']
        self.db.save(auction)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        auction = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(auction['awards'][0]['status'], 'unsuccessful')
        self.assertEqual(auction['awards'][1]['status'], 'pending.verification')
        self.assertEqual(auction['status'], 'active.qualification')
        self.assertNotIn('endDate', auction['awardPeriod'])

    def test_switch_active_to_unsuccessful(self):
        bid_token = self.initial_bids_tokens[self.award['bid_id']]
        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, self.award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, doc_id, self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

        response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "pending.payment"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "pending.payment")

        response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        auction = self.db.get(self.auction_id)
        auction['awards'][0]['signingPeriod']['endDate'] = auction['awards'][0]['signingPeriod']['startDate']
        self.db.save(auction)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        auction = response.json['data']
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(auction['awards'][0]['status'], 'unsuccessful')
        self.assertEqual(auction['contracts'][0]['status'], 'cancelled')
        self.assertEqual(auction['awards'][1]['status'], 'pending.verification')
        self.assertEqual(auction['status'], 'active.qualification')
        self.assertNotIn('endDate', auction['awardPeriod'])


@unittest.skip("option not available")
class AuctionLotAuctionPeriodResourceTest(AuctionAuctionPeriodResourceTest):
    initial_lots = test_lots


class AuctionComplaintSwitchResourceTest(BaseAuctionWebTest):

    def test_switch_to_pending(self):
        response = self.app.post_json('/auctions/{}/complaints'.format(self.auction_id), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': self.initial_organization,
            'status': 'claim'
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.json['data']['status'], 'claim')

        auction = self.db.get(self.auction_id)
        auction['complaints'][0]['dateSubmitted'] = (get_now() - timedelta(days=1 if 'procurementMethodDetails' in auction else 4)).isoformat()
        self.db.save(auction)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["complaints"][0]['status'], 'pending')

    def test_switch_to_complaint(self):
        for status in ['invalid', 'resolved', 'declined']:
            self.app.authorization = ('Basic', ('token', ''))
            response = self.app.post_json('/auctions/{}/complaints'.format(self.auction_id), {'data': {
                'title': 'complaint title',
                'description': 'complaint description',
                'author': self.initial_organization,
                'status': 'claim'
            }})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.json['data']['status'], 'claim')
            complaint = response.json['data']

            response = self.app.patch_json('/auctions/{}/complaints/{}?acc_token={}'.format(self.auction_id, complaint['id'], self.auction_token), {"data": {
                "status": "answered",
                "resolution": status * 4,
                "resolutionType": status
            }})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']["status"], "answered")
            self.assertEqual(response.json['data']["resolutionType"], status)

            auction = self.db.get(self.auction_id)
            auction['complaints'][-1]['dateAnswered'] = (get_now() - timedelta(days=1 if 'procurementMethodDetails' in auction else 4)).isoformat()
            self.db.save(auction)

            self.app.authorization = ('Basic', ('chronograph', ''))
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']["complaints"][-1]['status'], status)


@unittest.skip("option not available")
class AuctionLotComplaintSwitchResourceTest(AuctionComplaintSwitchResourceTest):
    initial_lots = test_lots


@unittest.skip("option not available")
class AuctionAwardComplaintSwitchResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(AuctionAwardComplaintSwitchResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']

    def test_switch_to_pending(self):
        response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(self.auction_id, self.award_id), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': self.initial_organization,
            'status': 'claim'
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.json['data']['status'], 'claim')

        response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        auction = self.db.get(self.auction_id)
        auction['awards'][0]['complaints'][0]['dateSubmitted'] = (get_now() - timedelta(days=1 if 'procurementMethodDetails' in auction else 4)).isoformat()
        self.db.save(auction)

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['awards'][0]["complaints"][0]['status'], 'pending')

    def test_switch_to_complaint(self):
        response = self.app.patch_json('/auctions/{}/awards/{}'.format(self.auction_id, self.award_id), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        for status in ['invalid', 'resolved', 'declined']:
            self.app.authorization = ('Basic', ('token', ''))
            response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(self.auction_id, self.award_id), {'data': {
                'title': 'complaint title',
                'description': 'complaint description',
                'author': self.initial_organization,
                'status': 'claim'
            }})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.json['data']['status'], 'claim')
            complaint = response.json['data']

            response = self.app.patch_json('/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(self.auction_id, self.award_id, complaint['id'], self.auction_token), {"data": {
                "status": "answered",
                "resolution": status * 4,
                "resolutionType": status
            }})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']["status"], "answered")
            self.assertEqual(response.json['data']["resolutionType"], status)

            auction = self.db.get(self.auction_id)
            auction['awards'][0]['complaints'][-1]['dateAnswered'] = (get_now() - timedelta(days=1 if 'procurementMethodDetails' in auction else 4)).isoformat()
            self.db.save(auction)

            self.app.authorization = ('Basic', ('chronograph', ''))
            response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['awards'][0]["complaints"][-1]['status'], status)


@unittest.skip("option not available")
class AuctionLotAwardComplaintSwitchResourceTest(AuctionAwardComplaintSwitchResourceTest):
    initial_lots = test_lots

    def setUp(self):
        super(AuctionAwardComplaintSwitchResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/auctions/{}/awards'.format(self.auction_id), {'data': {
            'suppliers': [self.initial_organization],
            'status': 'pending',
            'bid_id': self.initial_bids[0]['id'],
            'lotID': self.initial_bids[0]['lotValues'][0]['relatedLot']
        }})
        award = response.json['data']
        self.award_id = award['id']


class FinancialAuctionSwitchQualificationResourceTest(AuctionSwitchQualificationResourceTest):
    initial_bids = test_financial_bids[:1]
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionSwitchAuctionResourceTest(AuctionSwitchAuctionResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionSwitchUnsuccessfulResourceTest(AuctionSwitchUnsuccessfulResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotSwitchQualificationResourceTest(AuctionLotSwitchQualificationResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotSwitchAuctionResourceTest(AuctionLotSwitchAuctionResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotSwitchUnsuccessfulResourceTest(AuctionLotSwitchUnsuccessfulResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionAuctionPeriodResourceTest(AuctionAuctionPeriodResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotAuctionPeriodResourceTest(AuctionLotAuctionPeriodResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionComplaintSwitchResourceTest(AuctionComplaintSwitchResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotComplaintSwitchResourceTest(AuctionLotComplaintSwitchResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionAwardComplaintSwitchResourceTest(AuctionAwardComplaintSwitchResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotAwardComplaintSwitchResourceTest(AuctionLotAwardComplaintSwitchResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(AuctionComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(AuctionSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(AuctionSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(AuctionSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionSwitchUnsuccessfulResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
