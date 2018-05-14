# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    apply_patch,
    context_unpack,
    json_view,
    opresource,
    save_auction,
)
from openprocurement.auctions.dgf.validation import (
    validate_patch_auction_data,
)
from openprocurement.auctions.core.views.mixins import AuctionResource
from openprocurement.auctions.core.interfaces import IAuctionManager
from openprocurement.auctions.dgf.utils import (
    check_status,
)


@opresource(name='dgfOtherAssets:Auction',
            path='/auctions/{auction_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#auction for more info")
class AuctionResource(AuctionResource):

    @json_view(content_type="application/json", validators=(validate_patch_auction_data, ), permission='edit_auction')
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
        self.request.registry.getAdapter(self.context, IAuctionManager).change_auction(self.request)
        auction = self.context
        if self.request.authenticated_role != 'Administrator' and auction.status in ['complete', 'unsuccessful', 'cancelled']:
            self.request.errors.add('body', 'data', 'Can\'t update auction in current ({}) status'.format(auction.status))
            self.request.errors.status = 403
            return
        if self.request.authenticated_role == 'chronograph' and not auction.suspended:
            apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
            check_status(self.request)
            save_auction(self.request)
        else:
            apply_patch(self.request, src=self.request.validated['auction_src'])
        self.LOGGER.info('Updated auction {}'.format(auction.id),
                    extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_patch'}))
        return {'data': auction.serialize(auction.status)}
