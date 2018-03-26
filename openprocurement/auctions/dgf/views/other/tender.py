# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    context_unpack,
    json_view,
    APIResource,
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    opresource,
    save_auction,
)
from openprocurement.auctions.core.validation import (
    validate_patch_auction_data,
)
from openprocurement.auctions.dgf.utils import (
    check_status,
)


@opresource(
    name='dgfOtherAssets:Auction',
    path='/auctions/{auction_id}',
    auctionsprocurementMethodType="dgfOtherAssets",
    description="Open Contracting compatible data exchange format. ' \
    'See http://ocds.open-contracting.org/standard/r/master/#auction for more info")
class AuctionResource(APIResource):

    @json_view(permission='view_auction')
    def get(self):
        """Auction Read

        Get Auction
        ----------

        Example request to get auction:

        .. sourcecode:: http

            GET /auctions/64e93250be76435397e8c992ed4214d1 HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "id": "64e93250be76435397e8c992ed4214d1",
                    "auctionID": "UA-64e93250be76435397e8c992ed4214d1",
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "procuringEntity": {
                        "id": {
                            "name": "Державне управління справами",
                            "scheme": "https://ns.openprocurement.org/ua/edrpou",
                            "uid": "00037256",
                            "uri": "http://www.dus.gov.ua/"
                        },
                        "address": {
                            "countryName": "Україна",
                            "postalCode": "01220",
                            "region": "м. Київ",
                            "locality": "м. Київ",
                            "streetAddress": "вул. Банкова, 11, корпус 1"
                        }
                    },
                    "value": {
                        "amount": 500,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    },
                    "itemsToBeProcured": [
                        {
                            "description": "футляри до державних нагород",
                            "primaryClassification": {
                                "scheme": "CAV",
                                "id": "44617100-9",
                                "description": "Cartons"
                            },
                            "additionalClassification": [
                                {
                                    "scheme": "ДКПП",
                                    "id": "17.21.1",
                                    "description": "папір і картон гофровані, паперова й картонна тара"
                                }
                            ],
                            "unitOfMeasure": "item",
                            "quantity": 5
                        }
                    ],
                    "enquiryPeriod": {
                        "endDate": "2014-10-31T00:00:00"
                    },
                    "tenderPeriod": {
                        "startDate": "2014-11-03T00:00:00",
                        "endDate": "2014-11-06T10:00:00"
                    },
                    "awardPeriod": {
                        "endDate": "2014-11-13T00:00:00"
                    },
                    "deliveryDate": {
                        "endDate": "2014-11-20T00:00:00"
                    },
                    "minimalStep": {
                        "amount": 35,
                        "currency": "UAH"
                    }
                }
            }

        """
        if self.request.authenticated_role == 'chronograph':
            auction_data = self.context.serialize('chronograph_view')
        else:
            auction_data = self.context.serialize(self.context.status)
        return {'data': auction_data}

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_auction_data,
        ),
        permission='edit_auction')
    def patch(self):
        """Auction Edit (partial)

        For example here is how procuring entity can change number of items to be procured and total Value of a auction:

        .. sourcecode:: http

            PATCH /auctions/4879d3f8ee2443169b5fbbc9f89fa607 HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "value": {
                        "amount": 600
                    },
                    "itemsToBeProcured": [
                        {
                            "quantity": 6
                        }
                    ]
                }
            }

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "auctionID": "UA-64e93250be76435397e8c992ed4214d1",
                    "dateModified": "2014-10-27T08:12:34.956Z",
                    "value": {
                        "amount": 600
                    },
                    "itemsToBeProcured": [
                        {
                            "quantity": 6
                        }
                    ]
                }
            }

        """
        auction = self.context
        if self.request.authenticated_role != 'Administrator' and auction.status in [
                'complete', 'unsuccessful', 'cancelled']:
            self.request.errors.add(
                'body',
                'data',
                'Can\'t update auction in current ({}) status'.format(
                    auction.status))
            self.request.errors.status = 403
            return
        if self.request.authenticated_role == 'chronograph' and not auction.suspended:
            apply_patch(
                self.request,
                save=False,
                src=self.request.validated['auction_src'])
            check_status(self.request)
            save_auction(self.request)
        else:
            apply_patch(
                self.request,
                src=self.request.validated['auction_src'])
        self.LOGGER.info(
            'Updated auction {}'.format(
                auction.id), extra=context_unpack(
                self.request, {
                    'MESSAGE_ID': 'auction_patch'}))
        return {'data': auction.serialize(auction.status)}
