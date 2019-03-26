# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import get_now

# AuctionSwitchQualificationResourceTest


def switch_to_qualification(self):
    response = self.set_status('active.auction', {'status': self.initial_status})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/auctions/{}'.format(self.auction_id), {'data': {'id': self.auction_id}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "unsuccessful")
    self.assertNotIn("awards", response.json['data'])
