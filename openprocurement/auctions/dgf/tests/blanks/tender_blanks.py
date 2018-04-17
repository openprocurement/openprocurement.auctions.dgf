# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta, time
from iso8601 import parse_date

from openprocurement.auctions.core.constants import DGF_ELIGIBILITY_CRITERIA
from openprocurement.auctions.core.tests.base import JSON_RENDERER_ERROR
from openprocurement.auctions.core.utils import get_now, SANDBOX_MODE, TZ

from openprocurement.auctions.dgf.tests.base import test_financial_organization

# AuctionTest


def create_role(self):
    fields = set([
        'awardCriteriaDetails', 'awardCriteriaDetails_en', 'awardCriteriaDetails_ru',
        'description', 'description_en', 'description_ru', 'dgfID', 'tenderAttempts',
        'features', 'guarantee', 'hasEnquiries', 'items', 'lots', 'minimalStep', 'mode',
        'procurementMethodRationale', 'procurementMethodRationale_en', 'procurementMethodRationale_ru',
        'procurementMethodType', 'procuringEntity', 'merchandisingObject',
        'submissionMethodDetails', 'submissionMethodDetails_en', 'submissionMethodDetails_ru',
        'title', 'title_en', 'title_ru', 'value', 'auctionPeriod',
        'dgfDecisionDate', 'dgfDecisionID',
    ])
    if SANDBOX_MODE:
        fields.add('procurementMethodDetails')
    self.assertEqual(set(self.auction._fields) - self.auction._options.roles['create'].fields, fields)


def edit_role(self):
    fields = set([
        'features', 'hasEnquiries', 'description', 'description_en', 'description_ru',
        'title', 'title_en', 'title_ru', 'dgfID', 'dgfDecisionDate', 'dgfDecisionID', 'tenderAttempts',
    ])
    if SANDBOX_MODE:
        fields.add('procurementMethodDetails')
    self.assertEqual(set(self.auction._fields) - self.auction._options.roles['edit_active.tendering'].fields, fields)

# AuctionResourceTest


def create_auction_invalid(self):
    request_path = '/auctions'
    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description':
             u"Content-Type header should be one of ['application/json']", u'location': u'header',
         u'name': u'Content-Type'}
    ])

    response = self.app.post(
        request_path, 'data', content_type='application/json', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [JSON_RENDERER_ERROR])

    response = self.app.post_json(request_path, 'data', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'not_data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': []}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': {'procurementMethodType': 'invalid_value'}}, status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'procurementMethodType is not implemented', u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value',
                                                          'procurementMethodType': self.initial_data[
                                                              'procurementMethodType']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(request_path, {
        'data': {'value': 'invalid_value', 'procurementMethodType': self.initial_data['procurementMethodType']}},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [
            u'Please use a mapping for this field or Value instance instead of unicode.'], u'location': u'body',
            u'name': u'value'}
    ])

    response = self.app.post_json(request_path, {'data': {'procurementMethod': 'invalid_value',
                                                          'procurementMethodType': self.initial_data[
                                                              'procurementMethodType']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertIn({u'description': [u"Value must be one of ['open', 'selective', 'limited']."], u'location': u'body',
                   u'name': u'procurementMethod'}, response.json['errors'])
    # self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'tenderPeriod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'minimalStep'},
                  response.json['errors'])
    # self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'},
    #               response.json['errors'])
    # self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'enquiryPeriod'}, response.json['errors'])
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'value'},
                  response.json['errors'])
    # self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'},
    #               response.json['errors'])

    response = self.app.post_json(request_path, {'data': {'enquiryPeriod': {'endDate': 'invalid_value'},
                                                          'procurementMethodType': self.initial_data[
                                                              'procurementMethodType']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'endDate': [u"Could not parse invalid_value. Should be ISO8601."]}, u'location': u'body',
         u'name': u'enquiryPeriod'}
    ])

    response = self.app.post_json(request_path, {'data': {'enquiryPeriod': {'endDate': '9999-12-31T23:59:59.999999'},
                                                          'procurementMethodType': self.initial_data[
                                                              'procurementMethodType']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'endDate': [u'date value out of range']}, u'location': u'body', u'name': u'enquiryPeriod'}
    ])

    self.initial_data['tenderPeriod'] = self.initial_data.pop('auctionPeriod')
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['auctionPeriod'] = self.initial_data.pop('tenderPeriod')
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'startDate': [u'This field is required.']}, u'location': u'body', u'name': u'auctionPeriod'}
    ])

    self.initial_data['tenderPeriod'] = {'startDate': '2014-10-31T00:00:00', 'endDate': '2014-10-01T00:00:00'}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data.pop('tenderPeriod')
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'startDate': [u'period should begin before its end']}, u'location': u'body',
         u'name': u'tenderPeriod'}
    ])

    # data = self.initial_data['tenderPeriod']
    # self.initial_data['tenderPeriod'] = {'startDate': '2014-10-31T00:00:00', 'endDate': '2015-10-01T00:00:00'}
    # response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    # self.initial_data['tenderPeriod'] = data
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    # {u'description': [u'period should begin after enquiryPeriod'], u'location': u'body', u'name': u'tenderPeriod'}
    # ])

    now = get_now()
    # self.initial_data['awardPeriod'] = {'startDate': now.isoformat(), 'endDate': now.isoformat()}
    # response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    # del self.initial_data['awardPeriod']
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    # {u'description': [u'period should begin after tenderPeriod'], u'location': u'body', u'name': u'awardPeriod'}
    # ])

    data = self.initial_data['auctionPeriod']
    self.initial_data['auctionPeriod'] = {'startDate': (now + timedelta(days=15)).isoformat(),
                                          'endDate': (now + timedelta(days=15)).isoformat()}
    self.initial_data['awardPeriod'] = {'startDate': (now + timedelta(days=14)).isoformat(),
                                        'endDate': (now + timedelta(days=14)).isoformat()}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['auctionPeriod'] = data
    del self.initial_data['awardPeriod']
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'period should begin after auctionPeriod'], u'location': u'body', u'name': u'awardPeriod'}
    ])

    data = self.initial_data['minimalStep']
    self.initial_data['minimalStep'] = {'amount': '1000.0'}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['minimalStep'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'value should be less than value of auction'], u'location': u'body', u'name': u'minimalStep'}
    ])

    data = self.initial_data['minimalStep']
    self.initial_data['minimalStep'] = {'amount': '100.0', 'valueAddedTaxIncluded': False}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['minimalStep'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of value of auction'],
         u'location': u'body', u'name': u'minimalStep'}
    ])

    data = self.initial_data['minimalStep']
    self.initial_data['minimalStep'] = {'amount': '100.0', 'currency': "USD"}
    response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    self.initial_data['minimalStep'] = data
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'currency should be identical to currency of value of auction'], u'location': u'body',
         u'name': u'minimalStep'}
    ])

    auction_data = deepcopy(self.initial_data)
    auction_data['value'] = {'amount': '100.0', 'currency': "USD"}
    auction_data['minimalStep'] = {'amount': '5.0', 'currency': "USD"}
    response = self.app.post_json(request_path, {'data': auction_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'currency should be only UAH'], u'location': u'body', u'name': u'value'}
    ])

    auction_data = deepcopy(self.initial_data)
    del auction_data["procuringEntity"]["contactPoint"]["telephone"]
    response = self.app.post_json(request_path, {'data': auction_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'contactPoint': {u'email': [u'telephone or email should be present']}}, u'location': u'body',
         u'name': u'procuringEntity'}
    ])

    auction_data = deepcopy(self.initial_data)

    del auction_data["items"]
    response = self.app.post_json(request_path, {'data': auction_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'}, response.json['errors'])


def required_dgf_id(self):
    data = self.initial_data.copy()
    del data['dgfID']
    response = self.app.post_json('/auctions', {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'],
                     [{"location": "body", "name": "dgfID", "description": ["This field is required."]}])

    data['dgfID'] = self.initial_data['dgfID']
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertIn('dgfID', auction)
    self.assertEqual(data['dgfID'], auction['dgfID'])


def create_auction_auctionPeriod(self):
    data = self.initial_data.copy()
    # tenderPeriod = data.pop('tenderPeriod')
    # data['auctionPeriod'] = {'startDate': tenderPeriod['endDate']}
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertIn('tenderPeriod', auction)
    self.assertIn('auctionPeriod', auction)
    self.assertNotIn('startDate', auction['auctionPeriod'])
    self.assertEqual(parse_date(data['auctionPeriod']['startDate']).date(),
                     parse_date(auction['auctionPeriod']['shouldStartAfter'], TZ).date())
    if SANDBOX_MODE:
        auction_startDate = parse_date(data['auctionPeriod']['startDate'], None)
        if not auction_startDate.tzinfo:
            auction_startDate = TZ.localize(auction_startDate)
        tender_endDate = parse_date(auction['tenderPeriod']['endDate'], None)
        if not tender_endDate.tzinfo:
            tender_endDate = TZ.localize(tender_endDate)
        self.assertLessEqual((auction_startDate - tender_endDate).total_seconds(), 70)
    else:
        self.assertEqual(parse_date(auction['tenderPeriod']['endDate']).date(),
                         parse_date(data['auctionPeriod']['startDate'], TZ).date() - timedelta(days=1))
        self.assertEqual(parse_date(auction['tenderPeriod']['endDate']).time(), time(20, 0))


def create_auction_generated(self):
    data = self.initial_data.copy()
    # del data['awardPeriod']
    data.update({'id': 'hash', 'doc_id': 'hash2', 'auctionID': 'hash3'})
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    for key in ['procurementMethodDetails', 'submissionMethodDetails']:
        if key in auction:
            auction.pop(key)
    self.assertEqual(set(auction), set([
        u'procurementMethodType', u'id', u'date', u'dateModified', u'auctionID', u'status', u'enquiryPeriod',
        u'tenderPeriod', u'minimalStep', u'items', u'value', u'procuringEntity', u'next_check', u'dgfID',
        u'procurementMethod', u'awardCriteria', u'submissionMethod', u'title', u'owner', u'auctionPeriod',
        u'dgfDecisionDate', u'dgfDecisionID', u'documents', u'tenderAttempts',
    ]))
    self.assertNotEqual(data['id'], auction['id'])
    self.assertNotEqual(data['doc_id'], auction['id'])
    self.assertNotEqual(data['auctionID'], auction['auctionID'])


def create_auction(self):
    response = self.app.get('/auctions')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/auctions', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    if self.initial_organization == test_financial_organization:
        self.assertEqual(set(auction) - set(self.initial_data), set([
            u'id', u'dateModified', u'auctionID', u'date', u'status', u'procurementMethod', 'documents',
            u'awardCriteria', u'submissionMethod', u'next_check', u'owner', u'enquiryPeriod', u'tenderPeriod',
            u'eligibilityCriteria_en', u'eligibilityCriteria', u'eligibilityCriteria_ru',
        ]))
    else:
        self.assertEqual(set(auction) - set(self.initial_data), set([
            u'id', u'dateModified', u'auctionID', u'date', u'status', u'procurementMethod', 'documents',
            u'awardCriteria', u'submissionMethod', u'next_check', u'owner', u'enquiryPeriod', u'tenderPeriod',
        ]))
    self.assertIn(auction['id'], response.headers['Location'])

    response = self.app.get('/auctions/{}'.format(auction['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(auction))
    self.assertEqual(response.json['data'], auction)

    response = self.app.post_json('/auctions?opt_jsonp=callback', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('callback({"', response.body)

    response = self.app.post_json('/auctions?opt_pretty=1', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)

    response = self.app.post_json('/auctions', {"data": self.initial_data, "options": {"pretty": True}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)

    auction_data = deepcopy(self.initial_data)
    auction_data['guarantee'] = {"amount": 100500, "currency": "USD"}
    response = self.app.post_json('/auctions', {'data': auction_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    data = response.json['data']
    self.assertIn('guarantee', data)
    self.assertEqual(data['guarantee']['amount'], 100500)
    self.assertEqual(data['guarantee']['currency'], "USD")

# AuctionProcessTest


def first_bid_auction(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty auctions listing
    response = self.app.get('/auctions')
    self.assertEqual(response.json['data'], [])
    # create auction
    response = self.app.post_json('/auctions',
                                  {"data": self.initial_data})
    auction_id = self.auction_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    # switch to active.tendering
    self.set_status('active.tendering')
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    if self.initial_organization == test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450},
                                                'qualified': True, 'eligible': True}})
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450},
                                                'qualified': True}})
    bid_id = response.json['data']['id']
    bid_token = response.json['access']['token']
    bids_tokens = {bid_id: bid_token}
    # create second bid
    self.app.authorization = ('Basic', ('broker', ''))
    if self.initial_organization == test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450},
                                                'qualified': True, 'eligible': True}})
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450},
                                                'qualified': True}})
    bids_tokens[response.json['data']['id']] = response.json['access']['token']
    # switch to active.auction
    self.set_status('active.auction')

    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/auctions/{}/auction'.format(auction_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction urls
    response = self.app.patch_json('/auctions/{}/auction'.format(auction_id),
                                   {
                                       'data': {
                                           'auctionUrl': 'https://auction.auction.url',
                                           'bids': [
                                               {
                                                   'id': i['id'],
                                                   'participationUrl': 'https://auction.auction.url/for_bid/{}'.format(
                                                       i['id'])
                                               }
                                               for i in auction_bids_data
                                           ]
                                       }
                                   })
    # view bid participationUrl
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/bids/{}?acc_token={}'.format(auction_id, bid_id, bid_token))
    self.assertEqual(response.json['data']['participationUrl'], 'https://auction.auction.url/for_bid/{}'.format(bid_id))

    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/auctions/{}/auction'.format(auction_id),
                                  {'data': {'bids': auction_bids_data}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending award
    award = [i for i in response.json['data'] if i['status'] == 'pending'][0]
    award_id = award['id']
    # Upload auction protocol
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, award_id, owner_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award_id, doc_id, owner_token),
        {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')
    self.assertEqual(response.json["data"]["author"], 'auction_owner')
    # set award as unsuccessful
    response = self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token),
                                   {"data": {"status": "unsuccessful"}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending award
    award2 = [i for i in response.json['data'] if i['status'] == 'pending'][0]
    award2_id = award2['id']
    self.assertNotEqual(award_id, award2_id)
    # create first award complaint
    # self.app.authorization = ('Basic', ('broker', ''))
    # response = self.app.post_json('/auctions/{}/awards/{}/complaints?acc_token={}'.format(auction_id, award_id, bid_token),
    #                               {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.initial_organization, 'status': 'claim'}})
    # complaint_id = response.json['data']['id']
    # complaint_owner_token = response.json['access']['token']
    # # create first award complaint #2
    # response = self.app.post_json('/auctions/{}/awards/{}/complaints?acc_token={}'.format(auction_id, award_id, bid_token),
    #                               {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.initial_organization}})
    # # answering claim
    # self.app.patch_json('/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(auction_id, award_id, complaint_id, owner_token), {"data": {
    #     "status": "answered",
    #     "resolutionType": "resolved",
    #     "resolution": "resolution text " * 2
    # }})
    # # satisfying resolution
    # self.app.patch_json('/auctions/{}/awards/{}/complaints/{}?acc_token={}'.format(auction_id, award_id, complaint_id, complaint_owner_token), {"data": {
    #     "satisfied": True,
    #     "status": "resolved"
    # }})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending award
    award = [i for i in response.json['data'] if i['status'] == 'pending'][0]
    award_id = award['id']
    # Upload auction protocol
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, award_id, owner_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award_id, doc_id, owner_token),
        {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')
    self.assertEqual(response.json["data"]["author"], 'auction_owner')
    # set award as active
    self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token),
                        {"data": {"status": "active"}})
    # get contract id
    response = self.app.get('/auctions/{}'.format(auction_id))
    contract_id = response.json['data']['contracts'][-1]['id']
    # create auction contract document for test
    response = self.app.post(
        '/auctions/{}/contracts/{}/documents?acc_token={}'.format(auction_id, contract_id, owner_token),
        upload_files=[('file', 'name.doc', 'content')], status=201)
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    # after stand slill period
    self.app.authorization = ('Basic', ('chronograph', ''))
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    auction = self.db.get(auction_id)
    for i in auction.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(auction)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(auction_id, contract_id, owner_token),
                        {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}'.format(auction_id))
    self.assertEqual(response.json['data']['status'], 'complete')

    response = self.app.post(
        '/auctions/{}/contracts/{}/documents?acc_token={}'.format(auction_id, contract_id, owner_token),
        upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add document in current (complete) auction status")

    response = self.app.patch_json(
        '/auctions/{}/contracts/{}/documents/{}?acc_token={}'.format(auction_id, contract_id, doc_id, owner_token),
        {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update document in current (complete) auction status")

    response = self.app.put(
        '/auctions/{}/contracts/{}/documents/{}?acc_token={}'.format(auction_id, contract_id, doc_id, owner_token),
        upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update document in current (complete) auction status")


def suspended_auction(self):
    self.app.authorization = ('Basic', ('broker', ''))
    # empty auctions listing
    response = self.app.get('/auctions')
    self.assertEqual(response.json['data'], [])
    # create auction
    auction_data = deepcopy(self.initial_data)
    auction_data['suspended'] = True
    response = self.app.post_json('/auctions',
                                  {"data": auction_data})
    auction_id = self.auction_id = response.json['data']['id']
    owner_token = response.json['access']['token']
    self.assertNotIn('suspended', response.json['data'])

    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": True}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')

    authorization = self.app.authorization
    self.app.authorization = ('Basic', ('administrator', ''))

    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['suspended'], True)
    self.assertNotIn('next_check', response.json['data'])

    self.app.authorization = authorization
    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": False}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')

    self.app.authorization = ('Basic', ('administrator', ''))

    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": False}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['suspended'], False)
    self.assertIn('next_check', response.json['data'])

    self.app.authorization = authorization
    # switch to active.tendering
    self.set_status('active.tendering')
    # create bid
    self.app.authorization = ('Basic', ('broker', ''))
    if self.initial_organization == test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450},
                                                'qualified': True, 'eligible': True}})
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450},
                                                'qualified': True}})
    bid_id = response.json['data']['id']
    bid_token = response.json['access']['token']
    # create second bid
    self.app.authorization = ('Basic', ('broker', ''))
    if self.initial_organization == test_financial_organization:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450},
                                                'qualified': True, 'eligible': True}})
    else:
        response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                      {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450},
                                                'qualified': True}})

    authorization = self.app.authorization
    self.app.authorization = ('Basic', ('administrator', ''))

    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['suspended'], True)
    self.assertNotIn('next_check', response.json['data'])

    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": False}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['suspended'], False)
    self.assertIn('next_check', response.json['data'])

    self.app.authorization = authorization

    # switch to active.auction
    self.set_status('active.auction')

    # get auction info
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/auctions/{}/auction'.format(auction_id))
    auction_bids_data = response.json['data']['bids']
    # posting auction urls
    response = self.app.patch_json('/auctions/{}/auction'.format(auction_id),
                                   {
                                       'data': {
                                           'auctionUrl': 'https://auction.auction.url',
                                           'bids': [
                                               {
                                                   'id': i['id'],
                                                   'participationUrl': 'https://auction.auction.url/for_bid/{}'.format(
                                                       i['id'])
                                               }
                                               for i in auction_bids_data
                                           ]
                                       }
                                   })
    # view bid participationUrl
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/bids/{}?acc_token={}'.format(auction_id, bid_id, bid_token))
    self.assertEqual(response.json['data']['participationUrl'], 'https://auction.auction.url/for_bid/{}'.format(bid_id))

    # posting auction results
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/auctions/{}/auction'.format(auction_id),
                                  {'data': {'bids': auction_bids_data}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))

    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

    authorization = self.app.authorization
    self.app.authorization = ('Basic', ('administrator', ''))

    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['suspended'], True)
    self.assertNotIn('next_check', response.json['data'])

    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": False}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['suspended'], False)

    self.app.authorization = authorization
    # set award as unsuccessful
    response = self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token),
                                   {"data": {"status": "unsuccessful"}})
    # get awards
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending award
    award2_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
    self.assertNotEqual(award_id, award2_id)

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
    # get pending award
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

    response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
        self.auction_id, award_id, owner_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
    doc_id = response.json["data"]['id']

    response = self.app.patch_json(
        '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(auction_id, award_id, doc_id, owner_token),
        {"data": {"documentType": 'auctionProtocol'}})

    authorization = self.app.authorization
    self.app.authorization = ('Basic', ('administrator', ''))

    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['suspended'], True)
    self.assertNotIn('next_check', response.json['data'])

    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": False}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['suspended'], False)

    self.app.authorization = authorization

    self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token),
                        {"data": {"status": "active"}})
    # get contract id
    response = self.app.get('/auctions/{}'.format(auction_id))
    contract_id = response.json['data']['contracts'][-1]['id']

    authorization = self.app.authorization
    self.app.authorization = ('Basic', ('administrator', ''))

    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['suspended'], True)
    self.assertNotIn('next_check', response.json['data'])

    response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"suspended": False}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['suspended'], False)

    self.app.authorization = authorization

    # create auction contract document for test
    response = self.app.post(
        '/auctions/{}/contracts/{}/documents?acc_token={}'.format(auction_id, contract_id, owner_token),
        upload_files=[('file', 'name.doc', 'content')], status=201)
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    # after stand slill period
    self.app.authorization = ('Basic', ('chronograph', ''))
    self.set_status('complete', {'status': 'active.awarded'})
    # time travel
    auction = self.db.get(auction_id)
    for i in auction.get('awards', []):
        i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
    self.db.save(auction)
    # sign contract
    self.app.authorization = ('Basic', ('broker', ''))
    self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(auction_id, contract_id, owner_token),
                        {"data": {"status": "active"}})
    # check status
    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.get('/auctions/{}'.format(auction_id))
    self.assertEqual(response.json['data']['status'], 'complete')

# FinancialAuctionResourceTest


def create_auction_generated_financial(self):
    data = self.initial_data.copy()
    #del data['awardPeriod']
    data.update({'id': 'hash', 'doc_id': 'hash2', 'auctionID': 'hash3'})
    response = self.app.post_json('/auctions', {'data': data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    for key in ['procurementMethodDetails', 'submissionMethodDetails']:
        if key in auction:
            auction.pop(key)
    self.assertEqual(set(auction), set([
        u'procurementMethodType', u'id', u'date', u'dateModified', u'auctionID', u'status', u'enquiryPeriod',
        u'tenderPeriod', u'minimalStep', u'items', u'value', u'procuringEntity', u'next_check', u'dgfID',
        u'procurementMethod', u'awardCriteria', u'submissionMethod', u'title', u'owner', u'auctionPeriod',
        u'eligibilityCriteria', u'eligibilityCriteria_en', u'eligibilityCriteria_ru', 'documents',
        u'dgfDecisionDate', u'dgfDecisionID', u'tenderAttempts',
    ]))
    self.assertNotEqual(data['id'], auction['id'])
    self.assertNotEqual(data['doc_id'], auction['id'])
    self.assertNotEqual(data['auctionID'], auction['auctionID'])

    self.assertEqual(auction['eligibilityCriteria'], DGF_ELIGIBILITY_CRITERIA['ua'])
    self.assertEqual(auction['eligibilityCriteria_en'], DGF_ELIGIBILITY_CRITERIA['en'])
    self.assertEqual(auction['eligibilityCriteria_ru'], DGF_ELIGIBILITY_CRITERIA['ru'])
