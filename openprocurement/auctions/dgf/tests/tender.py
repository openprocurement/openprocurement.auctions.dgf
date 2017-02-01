# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from datetime import timedelta, time
from uuid import uuid4
from iso8601 import parse_date

from openprocurement.api.utils import ROUTE_PREFIX
from openprocurement.api.models import get_now, SANDBOX_MODE, TZ
from openprocurement.auctions.dgf.models import DGFOtherAssets, DGFFinancialAssets, DGF_ID_REQUIRED_FROM
from openprocurement.auctions.dgf.tests.base import (
    test_auction_data, test_financial_auction_data,
    test_organization, test_financial_organization,
    BaseWebTest, BaseAuctionWebTest,
    test_financial_auction_data_with_schema, test_auction_data_with_schema)

class AuctionTest(BaseWebTest):
    auction = DGFOtherAssets
    initial_data = test_auction_data

    def test_simple_add_auction(self):

        u = self.auction(self.initial_data)
        u.auctionID = "UA-EA-X"

        assert u.id is None
        assert u.rev is None

        u.store(self.db)

        assert u.id is not None
        assert u.rev is not None

        fromdb = self.db.get(u.id)

        assert u.auctionID == fromdb['auctionID']
        assert u.doc_type == "Auction"

        u.delete_instance(self.db)

    def test_create_role(self):
        fields = set([
            'awardCriteriaDetails', 'awardCriteriaDetails_en', 'awardCriteriaDetails_ru',
            'description', 'description_en', 'description_ru', 'dgfID', 'tenderAttempts',
            'features', 'guarantee', 'hasEnquiries', 'items', 'lots', 'minimalStep', 'mode',
            'procurementMethodRationale', 'procurementMethodRationale_en', 'procurementMethodRationale_ru',
            'procurementMethodType', 'procuringEntity',
            'submissionMethodDetails', 'submissionMethodDetails_en', 'submissionMethodDetails_ru',
            'title', 'title_en', 'title_ru', 'value', 'auctionPeriod',
            'dgfDecisionDate', 'dgfDecisionID',
        ])
        if SANDBOX_MODE:
            fields.add('procurementMethodDetails')
        self.assertEqual(set(self.auction._fields) - self.auction._options.roles['create'].fields, fields)

    def test_edit_role(self):
        fields = set([
            'features', 'hasEnquiries'
        ])
        if SANDBOX_MODE:
            fields.add('procurementMethodDetails')
        self.assertEqual(set(self.auction._fields) - self.auction._options.roles['edit_active.tendering'].fields, fields)


class AuctionResourceTest(BaseWebTest):
    initial_data = test_auction_data
    initial_organization = test_organization

    def test_empty_listing(self):
        response = self.app.get('/auctions')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertNotIn('{\n    "', response.body)
        self.assertNotIn('callback({', response.body)
        self.assertEqual(response.json['next_page']['offset'], '')
        self.assertNotIn('prev_page', response.json)

        response = self.app.get('/auctions?opt_jsonp=callback')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertNotIn('{\n    "', response.body)
        self.assertIn('callback({', response.body)

        response = self.app.get('/auctions?opt_pretty=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "', response.body)
        self.assertNotIn('callback({', response.body)

        response = self.app.get('/auctions?opt_jsonp=callback&opt_pretty=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('{\n    "', response.body)
        self.assertIn('callback({', response.body)

        response = self.app.get('/auctions?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertIn('descending=1', response.json['next_page']['uri'])
        self.assertIn('limit=10', response.json['next_page']['uri'])
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertIn('limit=10', response.json['prev_page']['uri'])

        response = self.app.get('/auctions?feed=changes')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertEqual(response.json['next_page']['offset'], '')
        self.assertNotIn('prev_page', response.json)

        response = self.app.get('/auctions?feed=changes&offset=0', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Offset expired/invalid', u'location': u'params', u'name': u'offset'}
        ])

        response = self.app.get('/auctions?feed=changes&descending=1&limit=10')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], [])
        self.assertIn('descending=1', response.json['next_page']['uri'])
        self.assertIn('limit=10', response.json['next_page']['uri'])
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertIn('limit=10', response.json['prev_page']['uri'])

    def test_listing(self):
        response = self.app.get('/auctions')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        auctions = []

        for i in range(3):
            offset = get_now().isoformat()
            response = self.app.post_json('/auctions', {'data': self.initial_data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            auctions.append(response.json['data'])

        ids = ','.join([i['id'] for i in auctions])

        while True:
            response = self.app.get('/auctions')
            self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
            if len(response.json['data']) == 3:
                break

        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in auctions]))
        self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in auctions]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in auctions]))

        while True:
            response = self.app.get('/auctions?offset={}'.format(offset))
            self.assertEqual(response.status, '200 OK')
            if len(response.json['data']) == 1:
                break
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get('/auctions?limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('prev_page', response.json)
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.get('/auctions', params=[('opt_fields', 'status')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
        self.assertIn('opt_fields=status', response.json['next_page']['uri'])

        response = self.app.get('/auctions', params=[('opt_fields', 'status,enquiryPeriod')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status', u'enquiryPeriod']))
        self.assertIn('opt_fields=status%2CenquiryPeriod', response.json['next_page']['uri'])

        response = self.app.get('/auctions?descending=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in auctions]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in auctions], reverse=True))

        response = self.app.get('/auctions?descending=1&limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        test_auction_data2 = self.initial_data.copy()
        test_auction_data2['mode'] = 'test'
        response = self.app.post_json('/auctions', {'data': test_auction_data2})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        while True:
            response = self.app.get('/auctions?mode=test')
            self.assertEqual(response.status, '200 OK')
            if len(response.json['data']) == 1:
                break
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get('/auctions?mode=_all_')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 4)

    def test_listing_changes(self):
        response = self.app.get('/auctions?feed=changes')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        auctions = []

        for i in range(3):
            response = self.app.post_json('/auctions', {'data': self.initial_data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            auctions.append(response.json['data'])

        ids = ','.join([i['id'] for i in auctions])

        while True:
            response = self.app.get('/auctions?feed=changes')
            self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
            if len(response.json['data']) == 3:
                break

        self.assertEqual(','.join([i['id'] for i in response.json['data']]), ids)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in auctions]))
        self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in auctions]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in auctions]))

        response = self.app.get('/auctions?feed=changes&limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('prev_page', response.json)
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.get('/auctions?feed=changes', params=[('opt_fields', 'status')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
        self.assertIn('opt_fields=status', response.json['next_page']['uri'])

        response = self.app.get('/auctions?feed=changes', params=[('opt_fields', 'status,enquiryPeriod')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status', u'enquiryPeriod']))
        self.assertIn('opt_fields=status%2CenquiryPeriod', response.json['next_page']['uri'])

        response = self.app.get('/auctions?feed=changes&descending=1')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in auctions]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in auctions], reverse=True))

        response = self.app.get('/auctions?feed=changes&descending=1&limit=2')
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('descending=1', response.json['prev_page']['uri'])
        self.assertEqual(len(response.json['data']), 0)

        test_auction_data2 = self.initial_data.copy()
        test_auction_data2['mode'] = 'test'
        response = self.app.post_json('/auctions', {'data': test_auction_data2})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        while True:
            response = self.app.get('/auctions?feed=changes&mode=test')
            self.assertEqual(response.status, '200 OK')
            if len(response.json['data']) == 1:
                break
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.get('/auctions?feed=changes&mode=_all_')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 4)

    def test_listing_draft(self):
        response = self.app.get('/auctions')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        auctions = []
        data = self.initial_data.copy()
        data.update({'status': 'draft'})

        for i in range(3):
            response = self.app.post_json('/auctions', {'data': self.initial_data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            auctions.append(response.json['data'])
            response = self.app.post_json('/auctions', {'data': data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')

        ids = ','.join([i['id'] for i in auctions])

        while True:
            response = self.app.get('/auctions')
            self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
            if len(response.json['data']) == 3:
                break

        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
        self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in auctions]))
        self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in auctions]))
        self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in auctions]))

    def test_create_auction_invalid(self):
        request_path = '/auctions'
        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
        ])

        response = self.app.post(
            request_path, 'data', content_type='application/json', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'No JSON object could be decoded',
                u'location': u'body', u'name': u'data'}
        ])

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
            {u'description': u'Not implemented', u'location': u'data', u'name': u'procurementMethodType'}
        ])

        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value', 'procurementMethodType': self.initial_data['procurementMethodType']}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        response = self.app.post_json(request_path, {'data': {'value': 'invalid_value', 'procurementMethodType': self.initial_data['procurementMethodType']}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [
                u'Please use a mapping for this field or Value instance instead of unicode.'], u'location': u'body', u'name': u'value'}
        ])

        response = self.app.post_json(request_path, {'data': {'procurementMethod': 'invalid_value', 'procurementMethodType': self.initial_data['procurementMethodType']}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertIn({u'description': [u"Value must be one of ['open', 'selective', 'limited']."], u'location': u'body', u'name': u'procurementMethod'}, response.json['errors'])
        #self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'tenderPeriod'}, response.json['errors'])
        self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'minimalStep'}, response.json['errors'])
        self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'}, response.json['errors'])
        #self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'enquiryPeriod'}, response.json['errors'])
        self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'value'}, response.json['errors'])
        self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'items'}, response.json['errors'])

        response = self.app.post_json(request_path, {'data': {'enquiryPeriod': {'endDate': 'invalid_value'}, 'procurementMethodType': self.initial_data['procurementMethodType']}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'endDate': [u"Could not parse invalid_value. Should be ISO8601."]}, u'location': u'body', u'name': u'enquiryPeriod'}
        ])

        response = self.app.post_json(request_path, {'data': {'enquiryPeriod': {'endDate': '9999-12-31T23:59:59.999999'}, 'procurementMethodType': self.initial_data['procurementMethodType']}}, status=422)
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
            {u'description': {u'startDate': [u'period should begin before its end']}, u'location': u'body', u'name': u'tenderPeriod'}
        ])

        #data = self.initial_data['tenderPeriod']
        #self.initial_data['tenderPeriod'] = {'startDate': '2014-10-31T00:00:00', 'endDate': '2015-10-01T00:00:00'}
        #response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
        #self.initial_data['tenderPeriod'] = data
        #self.assertEqual(response.status, '422 Unprocessable Entity')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertEqual(response.json['status'], 'error')
        #self.assertEqual(response.json['errors'], [
            #{u'description': [u'period should begin after enquiryPeriod'], u'location': u'body', u'name': u'tenderPeriod'}
        #])

        now = get_now()
        #self.initial_data['awardPeriod'] = {'startDate': now.isoformat(), 'endDate': now.isoformat()}
        #response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
        #del self.initial_data['awardPeriod']
        #self.assertEqual(response.status, '422 Unprocessable Entity')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertEqual(response.json['status'], 'error')
        #self.assertEqual(response.json['errors'], [
            #{u'description': [u'period should begin after tenderPeriod'], u'location': u'body', u'name': u'awardPeriod'}
        #])

        data = self.initial_data['auctionPeriod']
        self.initial_data['auctionPeriod'] = {'startDate': (now + timedelta(days=15)).isoformat(), 'endDate': (now + timedelta(days=15)).isoformat()}
        self.initial_data['awardPeriod'] = {'startDate': (now + timedelta(days=14)).isoformat(), 'endDate': (now + timedelta(days=14)).isoformat()}
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
            {u'description': [u'valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of value of auction'], u'location': u'body', u'name': u'minimalStep'}
        ])

        data = self.initial_data['minimalStep']
        self.initial_data['minimalStep'] = {'amount': '100.0', 'currency': "USD"}
        response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
        self.initial_data['minimalStep'] = data
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'currency should be identical to currency of value of auction'], u'location': u'body', u'name': u'minimalStep'}
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

        data = self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
        del self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
        response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
        self.initial_data["procuringEntity"]["contactPoint"]["telephone"] = data
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': {u'email': [u'telephone or email should be present']}}, u'location': u'body', u'name': u'procuringEntity'}
        ])

    @unittest.skipIf(get_now() < DGF_ID_REQUIRED_FROM, "Can`t create auction without dgfID only from {}".format(DGF_ID_REQUIRED_FROM))
    def test_required_dgf_id(self):
        data = self.initial_data.copy()
        del data['dgfID']
        response = self.app.post_json('/auctions', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [{"location": "body", "name": "dgfID", "description": ["This field is required."]}])

        data['dgfID'] = self.initial_data['dgfID']
        response = self.app.post_json('/auctions', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        self.assertIn('dgfID', auction)
        self.assertEqual(data['dgfID'], auction['dgfID'])


    def test_create_auction_auctionPeriod(self):
        data = self.initial_data.copy()
        #tenderPeriod = data.pop('tenderPeriod')
        #data['auctionPeriod'] = {'startDate': tenderPeriod['endDate']}
        response = self.app.post_json('/auctions', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        self.assertIn('tenderPeriod', auction)
        self.assertIn('auctionPeriod', auction)
        self.assertNotIn('startDate', auction['auctionPeriod'])
        self.assertEqual(parse_date(data['auctionPeriod']['startDate']).date(), parse_date(auction['auctionPeriod']['shouldStartAfter'], TZ).date())
        if SANDBOX_MODE:
            auction_startDate = parse_date(data['auctionPeriod']['startDate'], None)
            if not auction_startDate.tzinfo:
                auction_startDate = TZ.localize(auction_startDate)
            tender_endDate = parse_date(auction['tenderPeriod']['endDate'], None)
            if not tender_endDate.tzinfo:
                tender_endDate = TZ.localize(tender_endDate)
            self.assertLessEqual((auction_startDate - tender_endDate).total_seconds(), 70)
        else:
            self.assertEqual(parse_date(auction['tenderPeriod']['endDate']).date(), parse_date(data['auctionPeriod']['startDate'], TZ).date() - timedelta(days=1))
            self.assertEqual(parse_date(auction['tenderPeriod']['endDate']).time(), time(20, 0))

    def test_create_auction_generated(self):
        data = self.initial_data.copy()
        #del data['awardPeriod']
        data.update({'id': 'hash', 'doc_id': 'hash2', 'auctionID': 'hash3'})
        response = self.app.post_json('/auctions', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        if 'procurementMethodDetails' in auction:
            auction.pop('procurementMethodDetails')
        self.assertEqual(set(auction), set([
            u'procurementMethodType', u'id', u'date', u'dateModified', u'auctionID', u'status', u'enquiryPeriod',
            u'tenderPeriod', u'minimalStep', u'items', u'value', u'procuringEntity', u'next_check', u'dgfID',
            u'procurementMethod', u'awardCriteria', u'submissionMethod', u'title', u'owner', u'auctionPeriod',
            u'dgfDecisionDate', u'dgfDecisionID', u'documents', u'tenderAttempts',
        ]))
        self.assertNotEqual(data['id'], auction['id'])
        self.assertNotEqual(data['doc_id'], auction['id'])
        self.assertNotEqual(data['auctionID'], auction['auctionID'])

    def test_create_auction_draft(self):
        data = self.initial_data.copy()
        data.update({'status': 'draft'})
        response = self.app.post_json('/auctions', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        self.assertEqual(auction['status'], 'draft')

        response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'value': {'amount': 100}}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u"Can't update auction in current (draft) status", u'location': u'body', u'name': u'data'}
        ])

        response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.tendering'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        self.assertEqual(auction['status'], 'active.tendering')

        response = self.app.get('/auctions/{}'.format(auction['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        self.assertEqual(auction['status'], 'active.tendering')

    def test_create_auction(self):
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

    def test_get_auction(self):
        response = self.app.get('/auctions')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/auctions', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        auction = response.json['data']

        response = self.app.get('/auctions/{}'.format(auction['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], auction)

        response = self.app.get('/auctions/{}?opt_jsonp=callback'.format(auction['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('callback({"data": {"', response.body)

        response = self.app.get('/auctions/{}?opt_pretty=1'.format(auction['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('{\n    "data": {\n        "', response.body)

    @unittest.skip("option not available")
    def test_auction_features_invalid(self):
        data = self.initial_data.copy()
        item = data['items'][0].copy()
        item['id'] = "1"
        data['items'] = [item, item.copy()]
        response = self.app.post_json('/auctions', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Item id should be uniq for all items'], u'location': u'body', u'name': u'items'}
        ])
        data['items'][0]["id"] = "0"
        data['features'] = [
            {
                "code": "OCDS-123454-AIR-INTAKE",
                "featureOf": "lot",
                "title": u"Потужність всмоктування",
                "enum": [
                    {
                        "value": 0.1,
                        "title": u"До 1000 Вт"
                    },
                    {
                        "value": 0.15,
                        "title": u"Більше 1000 Вт"
                    }
                ]
            }
        ]
        response = self.app.post_json('/auctions', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedItem': [u'This field is required.']}], u'location': u'body', u'name': u'features'}
        ])
        data['features'][0]["relatedItem"] = "2"
        response = self.app.post_json('/auctions', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedItem': [u'relatedItem should be one of lots']}], u'location': u'body', u'name': u'features'}
        ])
        data['features'][0]["featureOf"] = "item"
        response = self.app.post_json('/auctions', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedItem': [u'relatedItem should be one of items']}], u'location': u'body', u'name': u'features'}
        ])
        data['features'][0]["relatedItem"] = "1"
        data['features'][0]["enum"][0]["value"] = 0.5
        response = self.app.post_json('/auctions', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'enum': [{u'value': [u'Float value should be less than 0.3.']}]}], u'location': u'body', u'name': u'features'}
        ])
        data['features'][0]["enum"][0]["value"] = 0.15
        response = self.app.post_json('/auctions', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'enum': [u'Feature value should be uniq for feature']}], u'location': u'body', u'name': u'features'}
        ])
        data['features'][0]["enum"][0]["value"] = 0.1
        data['features'].append(data['features'][0].copy())
        response = self.app.post_json('/auctions', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Feature code should be uniq for all features'], u'location': u'body', u'name': u'features'}
        ])
        data['features'][1]["code"] = u"OCDS-123454-YEARS"
        data['features'][1]["enum"][0]["value"] = 0.2
        response = self.app.post_json('/auctions', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Sum of max value of all features should be less then or equal to 30%'], u'location': u'body', u'name': u'features'}
        ])

    @unittest.skip("option not available")
    def test_auction_features(self):
        data = self.initial_data.copy()
        item = data['items'][0].copy()
        item['id'] = "1"
        data['items'] = [item]
        data['features'] = [
            {
                "code": "OCDS-123454-AIR-INTAKE",
                "featureOf": "item",
                "relatedItem": "1",
                "title": u"Потужність всмоктування",
                "title_en": u"Air Intake",
                "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 1000 Вт"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 1000 Вт"
                    }
                ]
            },
            {
                "code": "OCDS-123454-YEARS",
                "featureOf": "tenderer",
                "title": u"Років на ринку",
                "title_en": u"Years trading",
                "description": u"Кількість років, які організація учасник працює на ринку",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 3 років"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 3 років"
                    }
                ]
            },
            {
                "code": "OCDS-123454-POSTPONEMENT",
                "featureOf": "tenderer",
                "title": u"Відстрочка платежу",
                "title_en": u"Postponement of payment",
                "description": u"Термін відстрочки платежу",
                "enum": [
                    {
                        "value": 0.05,
                        "title": u"До 90 днів"
                    },
                    {
                        "value": 0.1,
                        "title": u"Більше 90 днів"
                    }
                ]
            }
        ]
        response = self.app.post_json('/auctions', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        self.assertEqual(auction['features'], data['features'])

        response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'features': [{
            "featureOf": "tenderer",
            "relatedItem": None
        }, {}, {}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('features', response.json['data'])
        self.assertNotIn('relatedItem', response.json['data']['features'][0])

        response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'tenderPeriod': {'startDate': None}}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('features', response.json['data'])

        response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'features': []}})
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('features', response.json['data'])

    @unittest.skip("this test requires fixed version of jsonpatch library")
    def test_patch_tender_jsonpatch(self):
        response = self.app.post_json('/auctions', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        owner_token = response.json['access']['token']
        dateModified = tender.pop('dateModified')

        import random
        response = self.app.patch_json('/auctions/{}'.format(tender['id']),
                                       {'data': {'items': [{"additionalClassifications": [
                                           {
                                               "scheme": "ДКПП",
                                               "id": "{}".format(i),
                                               "description": "description #{}".format(i)
                                           }
                                           for i in random.sample(range(30), 25)
                                           ]}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/auctions/{}'.format(tender['id']),
                                       {'data': {'items': [{"additionalClassifications": [
                                           {
                                               "scheme": "ДКПП",
                                               "id": "{}".format(i),
                                               "description": "description #{}".format(i)
                                           }
                                           for i in random.sample(range(30), 20)
                                           ]}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

    def test_patch_auction(self):
        response = self.app.get('/auctions')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/auctions', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        auction = response.json['data']
        owner_token = response.json['access']['token']
        dateModified = auction.pop('dateModified')

        response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotEqual(response.json['data']['status'], 'cancelled')

        response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotEqual(response.json['data']['status'], 'cancelled')

        response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {'data': {'procuringEntity': {'kind': 'defense'}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('kind', response.json['data']['procuringEntity'])

        #response = self.app.patch_json('/auctions/{}'.format(
            #auction['id']), {'data': {'tenderPeriod': {'startDate': None}}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertNotIn('startDate', response.json['data']['tenderPeriod'])

        #response = self.app.patch_json('/auctions/{}'.format(
            #auction['id']), {'data': {'tenderPeriod': {'startDate': auction['enquiryPeriod']['endDate']}}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertIn('startDate', response.json['data']['tenderPeriod'])

        response = self.app.patch_json('/auctions/{}'.format(
            auction['id']), {'data': {'procurementMethodRationale': 'Open'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        new_auction = response.json['data']
        new_dateModified = new_auction.pop('dateModified')
        #auction['procurementMethodRationale'] = 'Open'
        self.assertEqual(auction, new_auction)
        self.assertEqual(dateModified, new_dateModified)

        response = self.app.patch_json('/auctions/{}'.format(
            auction['id']), {'data': {'dateModified': new_dateModified}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        new_auction2 = response.json['data']
        new_dateModified2 = new_auction2.pop('dateModified')
        self.assertEqual(new_auction, new_auction2)
        self.assertEqual(new_dateModified, new_dateModified2)

        revisions = self.db.get(auction['id']).get('revisions')
        self.assertEqual(revisions[-1][u'changes'][0]['op'], u'remove')
        self.assertEqual(revisions[-1][u'changes'][0]['path'], u'/procurementMethod')

        response = self.app.patch_json('/auctions/{}'.format(
            auction['id']), {'data': {'items': [self.initial_data['items'][0]]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        #response = self.app.patch_json('/auctions/{}'.format(
            #auction['id']), {'data': {'items': [{}, self.initial_data['items'][0]]}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')
        #item0 = response.json['data']['items'][0]
        #item1 = response.json['data']['items'][1]
        #self.assertNotEqual(item0.pop('id'), item1.pop('id'))
        #self.assertEqual(item0, item1)

        #response = self.app.patch_json('/auctions/{}'.format(
            #auction['id']), {'data': {'items': [{}]}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertEqual(len(response.json['data']['items']), 1)

        #response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'items': [{"classification": {
            #"scheme": u"CAV",
            #"id": u"04000000-8",
            #"description": u"Нерухоме майно"
        #}}]}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')

        #response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'items': [{"additionalClassifications": [auction['items'][0]["classification"]]}]}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/auctions/{}'.format(
            auction['id']), {'data': {'enquiryPeriod': {'endDate': new_dateModified2}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        new_auction = response.json['data']
        self.assertIn('startDate', new_auction['enquiryPeriod'])

        #response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {"data": {"guarantee": {"amount": 12, "valueAddedTaxIncluded": True}}}, status=422)
        #self.assertEqual(response.status, '422 Unprocessable Entity')
        #self.assertEqual(response.json['errors'][0], {u'description': {u'valueAddedTaxIncluded': u'Rogue field'}, u'location': u'body', u'name': u'guarantee'})

        #response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {"data": {"guarantee": {"amount": 12}}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertIn('guarantee', response.json['data'])
        #self.assertEqual(response.json['data']['guarantee']['amount'], 12)
        #self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

        #response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction['id'], owner_token), {"data": {"guarantee": {"currency": "USD"}}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.json['data']['guarantee']['currency'], 'USD')

        #response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.auction'}})
        #self.assertEqual(response.status, '200 OK')

        #response = self.app.get('/auctions/{}'.format(auction['id']))
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertIn('auctionUrl', response.json['data'])

        auction_data = self.db.get(auction['id'])
        auction_data['status'] = 'complete'
        self.db.save(auction_data)

        response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'status': 'active.auction'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update auction in current (complete) status")

    def test_dateModified_auction(self):
        response = self.app.get('/auctions')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.post_json('/auctions', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        auction = response.json['data']
        dateModified = auction['dateModified']

        response = self.app.get('/auctions/{}'.format(auction['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['dateModified'], dateModified)

        response = self.app.patch_json('/auctions/{}'.format(
            auction['id']), {'data': {'procurementMethodRationale': 'Open'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['dateModified'], dateModified)
        auction = response.json['data']
        dateModified = auction['dateModified']

        response = self.app.get('/auctions/{}'.format(auction['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], auction)
        self.assertEqual(response.json['data']['dateModified'], dateModified)

    def test_auction_not_found(self):
        response = self.app.get('/auctions')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)

        response = self.app.get('/auctions/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'auction_id'}
        ])

        response = self.app.patch_json(
            '/auctions/some_id', {'data': {}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'auction_id'}
        ])

        # put custom document object into database to check tender construction on non-Tender data
        data = {'contract': 'test', '_id': uuid4().hex}
        self.db.save(data)

        response = self.app.get('/auctions/{}'.format(data['_id']), status=404)
        self.assertEqual(response.status, '404 Not Found')

    def test_guarantee(self):
        data = deepcopy(self.initial_data)
        data['guarantee'] = {"amount": 100, "currency": "UAH"}
        response = self.app.post_json('/auctions', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 100)
        self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

    def test_auction_Administrator_change(self):
        response = self.app.post_json('/auctions', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        auction = response.json['data']

        response = self.app.post_json('/auctions/{}/questions'.format(auction['id']), {'data': {'title': 'question title', 'description': 'question description', 'author': self.initial_organization}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('administrator', ''))
        response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'mode': u'test', 'procuringEntity': {"identifier": {"id": "00000000"}}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['mode'], u'test')
        self.assertEqual(response.json['data']["procuringEntity"]["identifier"]["id"], "00000000")

        response = self.app.patch_json('/auctions/{}/questions/{}'.format(auction['id'], question['id']), {"data": {"answer": "answer"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [
            {"location": "url", "name": "role", "description": "Forbidden"}
        ])
        self.app.authorization = authorization

        response = self.app.post_json('/auctions', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        auction = response.json['data']

        response = self.app.post_json('/auctions/{}/cancellations'.format(auction['id']), {'data': {'reason': 'cancellation reason', 'status': 'active'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        self.app.authorization = ('Basic', ('administrator', ''))
        response = self.app.patch_json('/auctions/{}'.format(auction['id']), {'data': {'mode': u'test'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['mode'], u'test')


class AuctionProcessTest(BaseAuctionWebTest):
    #setUp = BaseWebTest.setUp
    def setUp(self):
        super(AuctionProcessTest.__bases__[0], self).setUp()

    @unittest.skip("option not available")
    def test_invalid_auction_conditions(self):
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
        # create compaint
        response = self.app.post_json('/auctions/{}/complaints'.format(auction_id),
                                      {'data': {'title': 'invalid conditions', 'description': 'description', 'author': self.initial_organization, 'status': 'claim'}})
        complaint_id = response.json['data']['id']
        complaint_owner_token = response.json['access']['token']
        # answering claim
        self.app.patch_json('/auctions/{}/complaints/{}?acc_token={}'.format(auction_id, complaint_id, owner_token), {"data": {
            "status": "answered",
            "resolutionType": "resolved",
            "resolution": "I will cancel the auction"
        }})
        # satisfying resolution
        self.app.patch_json('/auctions/{}/complaints/{}?acc_token={}'.format(auction_id, complaint_id, complaint_owner_token), {"data": {
            "satisfied": True,
            "status": "resolved"
        }})
        # cancellation
        self.app.post_json('/auctions/{}/cancellations?acc_token={}'.format(auction_id, owner_token), {'data': {
            'reason': 'invalid conditions',
            'status': 'active'
        }})
        # check status
        response = self.app.get('/auctions/{}'.format(auction_id))
        self.assertEqual(response.json['data']['status'], 'cancelled')

    def _test_one_valid_bid_auction(self):
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
        response = self.set_status('active.tendering', {"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}})
        self.assertIn("auctionPeriod", response.json['data'])
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                          {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                          {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True}})
        # switch to active.qualification
        self.set_status('active.auction', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"id": auction_id}})
        self.assertNotIn('auctionPeriod', response.json['data'])
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        award_date = [i['date'] for i in response.json['data'] if i['status'] == 'pending'][0]
        # set award as active
        response = self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token), {"data": {"status": "active"}})
        self.assertNotEqual(response.json['data']['date'], award_date)

        # get contract id
        response = self.app.get('/auctions/{}'.format(auction_id))
        contract_id = response.json['data']['contracts'][-1]['id']
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
        self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(auction_id, contract_id, owner_token), {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/auctions/{}'.format(auction_id))
        self.assertEqual(response.json['data']['status'], 'complete')

    def _test_one_invalid_bid_auction(self):
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
                                          {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                          {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True}})
        # switch to active.qualification
        self.set_status('active.auction', {"auctionPeriod": {"startDate": None}, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"id": auction_id}})
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        # set award as unsuccessful
        response = self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token),
                                       {"data": {"status": "unsuccessful"}})
        # time travel
        auction = self.db.get(auction_id)
        for i in auction.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(auction)
        # set auction status after stand slill period
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/auctions/{}'.format(auction_id), {"data": {"id": auction_id}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/auctions/{}'.format(auction_id))
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_first_bid_auction(self):
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
                                          {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                          {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True}})
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']
        bids_tokens = {bid_id: bid_token}
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                          {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(auction_id),
                                          {'data': {'tenderers': [self.initial_organization], "value": {"amount": 450}, 'qualified': True}})
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
                                                       'participationUrl': 'https://auction.auction.url/for_bid/{}'.format(i['id'])
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
        # get pending.verification award
        award = [i for i in response.json['data'] if i['status'] == 'pending.verification'][0]
        award_id = award['id']
        # Upload auction protocol
        self.app.authorization = ('Basic', ('broker', ''))
        bid_token = bids_tokens[award['bid_id']]
        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, award_id, bid_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']

        response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award_id, doc_id, bid_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')
        self.assertEqual(response.json["data"]["author"], 'bid_owner')
        # set award as unsuccessful
        response = self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token),
                                       {"data": {"status": "unsuccessful"}})
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/auctions/{}/awards?acc_token={}'.format(auction_id, owner_token))
        # get pending award
        award2 = [i for i in response.json['data'] if i['status'] == 'pending.verification'][0]
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
        award = [i for i in response.json['data'] if i['status'] == 'pending.verification'][0]
        award_id = award['id']
        # Upload auction protocol
        self.app.authorization = ('Basic', ('broker', ''))
        bid_token = bids_tokens[award['bid_id']]
        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, award_id, bid_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']

        response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award_id, doc_id, bid_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')
        self.assertEqual(response.json["data"]["author"], 'bid_owner')
        # set award as "pending.payment
        self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token), {"data": {"status": "pending.payment"}})
        # set award as active
        self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(auction_id, award_id, owner_token), {"data": {"status": "active"}})
        # get contract id
        response = self.app.get('/auctions/{}'.format(auction_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # create auction contract document for test
        response = self.app.post('/auctions/{}/contracts/{}/documents?acc_token={}'.format(auction_id, contract_id, owner_token), upload_files=[('file', 'name.doc', 'content')], status=201)
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
        self.app.patch_json('/auctions/{}/contracts/{}?acc_token={}'.format(auction_id, contract_id, owner_token), {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/auctions/{}'.format(auction_id))
        self.assertEqual(response.json['data']['status'], 'complete')

        response = self.app.post('/auctions/{}/contracts/{}/documents?acc_token={}'.format(auction_id, contract_id, owner_token), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) auction status")

        response = self.app.patch_json('/auctions/{}/contracts/{}/documents/{}?acc_token={}'.format(auction_id, contract_id, doc_id, owner_token), {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) auction status")

        response = self.app.put('/auctions/{}/contracts/{}/documents/{}?acc_token={}'.format(auction_id, contract_id, doc_id, owner_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) auction status")


class FinancialAuctionTest(AuctionTest):
    auction = DGFFinancialAssets


class FinancialAuctionResourceTest(AuctionResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization

    def test_create_auction_generated(self):
        data = self.initial_data.copy()
        #del data['awardPeriod']
        data.update({'id': 'hash', 'doc_id': 'hash2', 'auctionID': 'hash3'})
        response = self.app.post_json('/auctions', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        if 'procurementMethodDetails' in auction:
            auction.pop('procurementMethodDetails')
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

        self.assertEqual(auction['eligibilityCriteria'], u"До участі допускаються лише ліцензовані фінансові установи.")
        self.assertEqual(auction['eligibilityCriteria_en'], u"Only licensed financial institutions are eligible to participate.")
        self.assertEqual(auction['eligibilityCriteria_ru'], u"К участию допускаются только лицензированные финансовые учреждения.")


class FinancialAuctionProcessTest(AuctionProcessTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class AuctionSchemaResourceTest(AuctionResourceTest):
    initial_data = test_auction_data_with_schema

    def test_create_auction_with_bad_schemas_code(self):
        response = self.app.get('/auctions')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 0)
        bad_initial_data = deepcopy(self.initial_data)
        bad_initial_data['items'][0]['classification']['id'] = "42124210-6"
        response = self.app.post_json('/auctions', {"data": bad_initial_data},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'],
                         [{
                             "location": "body",
                             "name": "items",
                             "description": [{
                                 "schema_properties": ["classification id mismatch with schema_properties code"]
                             }]
                         }])


class AuctionSchemaProcessTest(AuctionProcessTest):
    initial_data = test_auction_data_with_schema


class FinancialAuctionSchemaResourceTest(FinancialAuctionResourceTest):
    initial_data = test_financial_auction_data_with_schema


class FinancialAuctionSchemaProcessTest(FinancialAuctionProcessTest):
    initial_data = test_financial_auction_data_with_schema


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionProcessTest))
    suite.addTest(unittest.makeSuite(AuctionResourceTest))
    suite.addTest(unittest.makeSuite(AuctionTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionProcessTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionTest))
    suite.addTest(unittest.makeSuite(AuctionSchemaResourceTest))
    suite.addTest(unittest.makeSuite(AuctionSchemaProcessTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionSchemaResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionSchemaProcessTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
