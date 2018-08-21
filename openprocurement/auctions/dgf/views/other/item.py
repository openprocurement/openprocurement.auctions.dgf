# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    apply_patch,
    context_unpack,
    get_now,
    json_view,
    opresource,
    save_auction,
)
from openprocurement.auctions.core.views.mixins import AuctionLotResource
from openprocurement.auctions.core.endpoints import ENDPOINTS
from openprocurement.auctions.dgf.validation import (
    validate_item_data,
)


@opresource(
    name='dgfOtherAssets:Auction Items',
    collection_path=ENDPOINTS['items'],
    path=ENDPOINTS['item'],
    auctionsprocurementMethodType="dgfOtherAssets",
    description="Auction items")
class AuctionLotResource(AuctionLotResource):

    @json_view(
        content_type="application/json",
        permission='edit_auction_items',
        validators=(validate_item_data))
    def collection_post(self):
        item = self.request.validated['item']
        self.context.items.append(item)
        if save_auction(self.request):
            self.LOGGER.info(
                'Created lot item {}'.format(item.id),
                extra=context_unpack(
                    self.request,
                    {'MESSAGE_ID': 'auction_item_create'},
                    {'item_id': item.id}
                )
            )
            self.request.response.status = 201
            item_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(
                _route_name=item_route,
                item_id=item.id,
                _query={}
            )
            return {'data': item.serialize("view")}

    @json_view(
        content_type="application/json",
        permission='view_auction')
    def get(self):
        item = self.context
        return {'data': item.serialize('view')}
