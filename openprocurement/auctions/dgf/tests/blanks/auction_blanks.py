# -*- coding: utf-8 -*-
from copy import deepcopy
from openprocurement.auctions.core.utils import get_now

# AuctionAuctionResourceTest


def post_auction_auction(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current (active.tendering) auction status")

    self.set_status('active.auction')

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id),
                                  {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[1]['id'],
                "value": {
                    "amount": 419,
                    "currency": "UAH",
                    "valueAddedTaxIncluded": True
                }
            }
        ]
    }

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Number of auction results did not match the number of auction bids")

    patch_data['bids'].append({
        "value": {
            "amount": 409,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        }
    })

    patch_data['bids'][1]['id'] = "some_id"

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][1]['id'] = "00000000000000000000000000000000"

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the auction bids")

    patch_data['bids'][1]['id'] = self.initial_bids[0]['id']

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertNotEqual(auction["bids"][0]['value']['amount'], self.initial_bids[0]['value']['amount'])
    self.assertNotEqual(auction["bids"][1]['value']['amount'], self.initial_bids[1]['value']['amount'])
    self.assertEqual(auction["bids"][0]['value']['amount'], patch_data["bids"][1]['value']['amount'])
    self.assertEqual(auction["bids"][1]['value']['amount'], patch_data["bids"][0]['value']['amount'])
    self.assertEqual('active.qualification', auction["status"])
    for i, status in enumerate(['pending', 'pending.waiting']):
        self.assertIn("tenderers", auction["bids"][i])
        self.assertIn("name", auction["bids"][i]["tenderers"][0])
        # self.assertIn(auction["awards"][0]["id"], response.headers['Location'])
        self.assertEqual(auction["awards"][i]['bid_id'], patch_data["bids"][i]['id'])
        self.assertEqual(auction["awards"][i]['value']['amount'], patch_data["bids"][i]['value']['amount'])
        self.assertEqual(auction["awards"][i]['suppliers'], self.initial_bids[i]['tenderers'])
        self.assertEqual(auction["awards"][i]['status'], status)
        if status == 'pending':
            self.assertIn("verificationPeriod", auction["awards"][i])

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current (active.qualification) auction status")

# AuctionBidInvalidationAuctionResourceTest


def post_auction_all_invalid_bids(self):
    self.app.authorization = ('Basic', ('auction', ''))

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id),
                                  {'data': {'bids': self.initial_bids}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']

    self.assertEqual(auction["bids"][0]['value']['amount'], self.initial_bids[0]['value']['amount'])
    self.assertEqual(auction["bids"][1]['value']['amount'], self.initial_bids[1]['value']['amount'])
    self.assertEqual(auction["bids"][2]['value']['amount'], self.initial_bids[2]['value']['amount'])

    value_threshold = auction['value']['amount'] + auction['minimalStep']['amount']
    self.assertLess(auction["bids"][0]['value']['amount'], value_threshold)
    self.assertLess(auction["bids"][1]['value']['amount'], value_threshold)
    self.assertLess(auction["bids"][2]['value']['amount'], value_threshold)
    self.assertEqual(auction["bids"][0]['status'], 'invalid')
    self.assertEqual(auction["bids"][1]['status'], 'invalid')
    self.assertEqual(auction["bids"][2]['status'], 'invalid')
    self.assertEqual('unsuccessful', auction["status"])


def post_auction_one_invalid_bid(self):
    self.app.authorization = ('Basic', ('auction', ''))

    bids = deepcopy(self.initial_bids)
    bids[0]['value']['amount'] = bids[0]['value']['amount'] * 3
    bids[1]['value']['amount'] = bids[1]['value']['amount'] * 2
    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': {'bids': bids}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']

    self.assertEqual(auction["bids"][0]['value']['amount'], bids[0]['value']['amount'])
    self.assertEqual(auction["bids"][1]['value']['amount'], bids[1]['value']['amount'])
    self.assertEqual(auction["bids"][2]['value']['amount'], bids[2]['value']['amount'])

    value_threshold = auction['value']['amount'] + auction['minimalStep']['amount']

    self.assertGreater(auction["bids"][0]['value']['amount'], value_threshold)
    self.assertGreater(auction["bids"][1]['value']['amount'], value_threshold)
    self.assertLess(auction["bids"][2]['value']['amount'], value_threshold)

    self.assertEqual(auction["bids"][0]['status'], 'active')
    self.assertEqual(auction["bids"][1]['status'], 'active')
    self.assertEqual(auction["bids"][2]['status'], 'invalid')

    self.assertEqual('active.qualification', auction["status"])

    for i, status in enumerate(['pending', 'pending.waiting']):
        self.assertIn("tenderers", auction["bids"][i])
        self.assertIn("name", auction["bids"][i]["tenderers"][0])
        # self.assertIn(auction["awards"][0]["id"], response.headers['Location'])
        self.assertEqual(auction["awards"][i]['bid_id'], bids[i]['id'])
        self.assertEqual(auction["awards"][i]['value']['amount'], bids[i]['value']['amount'])
        self.assertEqual(auction["awards"][i]['suppliers'], bids[i]['tenderers'])
        self.assertEqual(auction["awards"][i]['status'], status)
        if status == 'pending':
            self.assertIn("verificationPeriod", auction["awards"][i])


def post_auction_one_valid_bid(self):
    self.app.authorization = ('Basic', ('auction', ''))

    bids = deepcopy(self.initial_bids)
    bids[0]['value']['amount'] = bids[0]['value']['amount'] * 2
    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': {'bids': bids}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']

    self.assertEqual(auction["bids"][0]['value']['amount'], bids[0]['value']['amount'])
    self.assertEqual(auction["bids"][1]['value']['amount'], bids[1]['value']['amount'])
    self.assertEqual(auction["bids"][2]['value']['amount'], bids[2]['value']['amount'])

    value_threshold = auction['value']['amount'] + auction['minimalStep']['amount']

    self.assertGreater(auction["bids"][0]['value']['amount'], value_threshold)
    self.assertLess(auction["bids"][1]['value']['amount'], value_threshold)
    self.assertLess(auction["bids"][2]['value']['amount'], value_threshold)

    self.assertEqual(auction["bids"][0]['status'], 'active')
    self.assertEqual(auction["bids"][1]['status'], 'invalid')
    self.assertEqual(auction["bids"][2]['status'], 'invalid')

    self.assertEqual('active.qualification', auction["status"])

    for i, status in enumerate(['pending', 'unsuccessful']):
        self.assertIn("tenderers", auction["bids"][i])
        self.assertIn("name", auction["bids"][i]["tenderers"][0])
        # self.assertIn(auction["awards"][0]["id"], response.headers['Location'])
        self.assertEqual(auction["awards"][i]['bid_id'], bids[i]['id'])
        self.assertEqual(auction["awards"][i]['value']['amount'], bids[i]['value']['amount'])
        self.assertEqual(auction["awards"][i]['suppliers'], bids[i]['tenderers'])
        self.assertEqual(auction["awards"][i]['status'], status)
        if status == 'pending':
            self.assertIn("verificationPeriod", auction["awards"][i])

# AuctionLotAuctionResourceTest


def post_auction_auction_lot(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current (active.tendering) auction status")

    self.set_status('active.auction')

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id),
                                  {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[1]['id'],
                'lotValues': [
                    {
                        "value": {
                            "amount": 419,
                            "currency": "UAH",
                            "valueAddedTaxIncluded": True
                        }
                    }
                ]
            }
        ]
    }

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Number of auction results did not match the number of auction bids")

    patch_data['bids'].append({
        'lotValues': [
            {
                "value": {
                    "amount": 409,
                    "currency": "UAH",
                    "valueAddedTaxIncluded": True
                }
            }
        ]
    })

    patch_data['bids'][1]['id'] = "some_id"

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][1]['id'] = "00000000000000000000000000000000"

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the auction bids")

    patch_data['bids'][1]['id'] = self.initial_bids[0]['id']

    for lot in self.initial_lots:
        response = self.app.post_json('/auctions/{}/auction/{}'.format(self.auction_id, lot['id']),
                                      {'data': patch_data})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']

    self.assertNotEqual(auction["bids"][0]['lotValues'][0]['value']['amount'],
                        self.initial_bids[0]['lotValues'][0]['value']['amount'])
    self.assertNotEqual(auction["bids"][1]['lotValues'][0]['value']['amount'],
                        self.initial_bids[1]['lotValues'][0]['value']['amount'])
    self.assertEqual(auction["bids"][0]['lotValues'][0]['value']['amount'],
                     patch_data["bids"][1]['lotValues'][0]['value']['amount'])
    self.assertEqual(auction["bids"][1]['lotValues'][0]['value']['amount'],
                     patch_data["bids"][0]['lotValues'][0]['value']['amount'])
    self.assertEqual('active.qualification', auction["status"])
    for i, status in enumerate(['pending', 'pending.waiting']):
        self.assertIn("tenderers", auction["bids"][i])
        self.assertIn("name", auction["bids"][i]["tenderers"][0])
        # self.assertIn(auction["awards"][0]["id"], response.headers['Location'])
        self.assertEqual(auction["awards"][i]['bid_id'], patch_data["bids"][i]['id'])
        self.assertEqual(auction["awards"][i]['value']['amount'],
                         patch_data["bids"][i]['lotValues'][0]['value']['amount'])
        self.assertEqual(auction["awards"][i]['suppliers'], self.initial_bids[i]['tenderers'])
        self.assertEqual(auction["awards"][i]['status'], status)
        if status == 'pending':
            self.assertIn("verificationPeriod", auction["awards"][i])

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current (active.qualification) auction status")

# AuctionMultipleLotAuctionResourceTest


def post_auction_auction_2_lots(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current (active.tendering) auction status")

    self.set_status('active.auction')

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id),
                                  {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[1]['id'],
                'lotValues': [
                    {
                        "value": {
                            "amount": 419,
                            "currency": "UAH",
                            "valueAddedTaxIncluded": True
                        }
                    }
                ]
            }
        ]
    }

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Number of auction results did not match the number of auction bids")

    patch_data['bids'].append({
        'lotValues': [
            {
                "value": {
                    "amount": 409,
                    "currency": "UAH",
                    "valueAddedTaxIncluded": True
                }
            }
        ]
    })

    patch_data['bids'][1]['id'] = "some_id"

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][1]['id'] = "00000000000000000000000000000000"

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the auction bids")

    patch_data['bids'][1]['id'] = self.initial_bids[0]['id']

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     [{"lotValues": ["Number of lots of auction results did not match the number of auction lots"]}])

    for bid in patch_data['bids']:
        bid['lotValues'] = [bid['lotValues'][0].copy() for _ in self.initial_lots]

    patch_data['bids'][0]['lotValues'][1]['relatedLot'] = self.initial_bids[0]['lotValues'][0]['relatedLot']

    response = self.app.patch_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     [{u'lotValues': [{u'relatedLot': [u'relatedLot should be one of lots of bid']}]}])

    patch_data['bids'][0]['lotValues'][1]['relatedLot'] = self.initial_bids[0]['lotValues'][1]['relatedLot']

    for lot in self.initial_lots:
        response = self.app.post_json('/auctions/{}/auction/{}'.format(self.auction_id, lot['id']),
                                      {'data': patch_data})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']

    self.assertNotEqual(auction["bids"][0]['lotValues'][0]['value']['amount'],
                        self.initial_bids[0]['lotValues'][0]['value']['amount'])
    self.assertNotEqual(auction["bids"][1]['lotValues'][0]['value']['amount'],
                        self.initial_bids[1]['lotValues'][0]['value']['amount'])
    self.assertEqual(auction["bids"][0]['lotValues'][0]['value']['amount'],
                     patch_data["bids"][1]['lotValues'][0]['value']['amount'])
    self.assertEqual(auction["bids"][1]['lotValues'][0]['value']['amount'],
                     patch_data["bids"][0]['lotValues'][0]['value']['amount'])
    self.assertEqual('active.qualification', auction["status"])
    for i, status in enumerate(['pending', 'pending.waiting']):
        self.assertIn("tenderers", auction["bids"][i])
        self.assertIn("name", auction["bids"][i]["tenderers"][0])
        # self.assertIn(auction["awards"][0]["id"], response.headers['Location'])
        self.assertEqual(auction["awards"][i]['bid_id'], patch_data["bids"][i]['id'])
        self.assertEqual(auction["awards"][i]['value']['amount'],
                         patch_data["bids"][i]['lotValues'][0]['value']['amount'])
        self.assertEqual(auction["awards"][i]['suppliers'], self.initial_bids[i]['tenderers'])
        self.assertEqual(auction["awards"][i]['status'], status)
        if status == 'pending':
            self.assertIn("verificationPeriod", auction["awards"][i])

    response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current (active.qualification) auction status")


# DGFAuctionBridgePeriodPatch

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

    self.app.authorization = ('Basic', ('auction', ''))
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

    self.app.authorization = ('Basic', ('auction', ''))
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
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], 'active.auction')
    item = response.json['data']["lots"][0] if self.initial_lots else response.json['data']
    self.assertGreaterEqual(item['auctionPeriod']['shouldStartAfter'], response.json['data']['tenderPeriod']['endDate'])

    self.app.authorization = ('Basic', ('auction', ''))
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
