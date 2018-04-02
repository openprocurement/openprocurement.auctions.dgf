# -*- coding: utf-8 -*-
from openprocurement.api.models.auction_models.models import get_now

# AuctionSwitchQualificationResourceTest


def switch_to_qualification(self):
    response = self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")
    self.assertNotIn("awards", response.json['data'])

# AuctionAuctionPeriodResourceTest


def set_auction_period(self):
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
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'],
                            response.json['data']['tenderPeriod']['endDate'])
    self.assertIn('T00:00:00+', item['auctionPeriod']['shouldStartAfter'])
    self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

    if self.initial_lots:
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {
            'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id),
                                       {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00+00:00"}}})
        item = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(item['auctionPeriod']['startDate'], '9999-01-01T00:00:00+00:00')

    if self.initial_lots:
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id),
                                       {'data': {"lots": [{"auctionPeriod": {"startDate": None}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id),
                                       {'data': {"auctionPeriod": {"startDate": None}}})
        item = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('startDate', item['auctionPeriod'])


def reset_auction_period(self):
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
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id),
                                       {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id),
                                       {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
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
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id),
                                       {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id),
                                       {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
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
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {
            'data': {"lots": [{"auctionPeriod": {"startDate": response.json['data']['tenderPeriod']['endDate']}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {
            'data': {"auctionPeriod": {"startDate": response.json['data']['tenderPeriod']['endDate']}}})
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
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id),
                                       {'data': {"lots": [{"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}]}})
        item = response.json['data']["lots"][0]
    else:
        response = self.app.patch_json('/auctions/{}'.format(self.auction_id),
                                       {'data': {"auctionPeriod": {"startDate": "9999-01-01T00:00:00"}}})
        item = response.json['data']
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], 'active.auction')
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])
    self.assertIn('9999-01-01T00:00:00', item['auctionPeriod']['startDate'])
    self.assertIn('9999-01-01T00:00:00', response.json['data']['next_check'])
