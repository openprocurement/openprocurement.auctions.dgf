# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    cleanup_bids_for_cancelled_lots,
    APIResource,
)
from openprocurement.auctions.core.utils import (
    save_auction,
    apply_patch,
    add_next_award,
    opresource,
)
from openprocurement.auctions.core.validation import (
    validate_auction_auction_data,
)


@opresource(name='Auction Auction',
            collection_path='/auctions/{auction_id}/auction',
            path='/auctions/{auction_id}/auction/{auction_lot_id}',
            description="Auction auction data")
class AuctionAuctionResource(APIResource):

    @json_view(permission='auction')
    def collection_get(self):
        """Get auction info.

        Get auction auction info
        -----------------------

        Example request to get auction auction information:

        .. sourcecode:: http

            GET /auctions/4879d3f8ee2443169b5fbbc9f89fa607/auction HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "bids": [
                        {
                            "value": {
                                "amount": 500,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        },
                        {
                            "value": {
                                "amount": 485,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        }
                    ],
                    "minimalStep":{
                        "amount": 35,
                        "currency": "UAH"
                    },
                    "tenderPeriod":{
                        "startDate": "2014-11-04T08:00:00"
                    }
                }
            }

        """
        if self.request.validated['auction_status'] != 'active.auction':
            self.request.errors.add('body', 'data', 'Can\'t get auction info in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        return {'data': self.request.validated['auction'].serialize("auction_view")}

    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def collection_patch(self):
        """Set urls for access to auction.
        """
        if apply_patch(self.request, src=self.request.validated['auction_src']):
            self.LOGGER.info('Updated auction urls', extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_auction_patch'}))
            return {'data': self.request.validated['auction'].serialize("auction_view")}

    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def collection_post(self):
        """Report auction results.

        Report auction results
        ----------------------

        Example request to report auction results:

        .. sourcecode:: http

            POST /auctions/4879d3f8ee2443169b5fbbc9f89fa607/auction HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "bids": [
                        {
                            "value": {
                                "amount": 400,
                                "currency": "UAH"
                            }
                        },
                        {
                            "value": {
                                "amount": 385,
                                "currency": "UAH"
                            }
                        }
                    ]
                }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "bids": [
                        {
                            "value": {
                                "amount": 400,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        },
                        {
                            "value": {
                                "amount": 385,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        }
                    ],
                    "minimalStep":{
                        "amount": 35,
                        "currency": "UAH"
                    },
                    "tenderPeriod":{
                        "startDate": "2014-11-04T08:00:00"
                    }
                }
            }

        """
        apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
        if all([i.auctionPeriod and i.auctionPeriod.endDate for i in self.request.validated['auction'].lots if i.numberOfBids > 1 and i.status == 'active']):
            add_next_award(self.request)
        if save_auction(self.request):
            self.LOGGER.info('Report auction results', extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_auction_post'}))
            return {'data': self.request.validated['auction'].serialize(self.request.validated['auction'].status)}

    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def patch(self):
        """Set urls for access to auction for lot.
        """
        if apply_patch(self.request, src=self.request.validated['auction_src']):
            self.LOGGER.info('Updated auction urls', extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_lot_auction_patch'}))
            return {'data': self.request.validated['auction'].serialize("auction_view")}

    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def post(self):
        """Report auction results for lot.
        """
        apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
        if all([i.auctionPeriod and i.auctionPeriod.endDate for i in self.request.validated['auction'].lots if i.numberOfBids > 1 and i.status == 'active']):
            cleanup_bids_for_cancelled_lots(self.request.validated['auction'])
            add_next_award(self.request)
        if save_auction(self.request):
            self.LOGGER.info('Report auction results', extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_lot_auction_post'}))
            return {'data': self.request.validated['auction'].serialize(self.request.validated['auction'].status)}
