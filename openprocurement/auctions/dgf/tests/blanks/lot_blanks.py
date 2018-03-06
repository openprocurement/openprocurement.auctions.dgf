# -*- coding: utf-8 -*-

# AuctionLotResourceTest


def patch_auction_currency(self):
    # create lot
    response = self.app.post_json('/auctions/{}/lots'.format(self.auction_id), {'data': self.test_lots[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['value']['currency'], "UAH")

    # update auction currency without mimimalStep currency change
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {"data": {"value": {"currency": "GBP"}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'currency should be identical to currency of value of auction'],
         u'location': u'body', u'name': u'minimalStep'},
        {u"description": [u"currency should be only UAH"],
         u"location": u"body", u"name": u"value"}
    ])
