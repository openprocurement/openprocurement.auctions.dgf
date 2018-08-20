# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    apply_patch,
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
