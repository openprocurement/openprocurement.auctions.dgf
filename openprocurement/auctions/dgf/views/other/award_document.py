# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.core.awarding_2_0.views import (
    AuctionAwardDocumentResource as BaseAuctionAwardDocumentResource
)


@opresource(name='dgfOtherAssets:Auction Award Documents',
            collection_path='/auctions/{auction_id}/awards/{award_id}/documents',
            path='/auctions/{auction_id}/awards/{award_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction award documents")
class AuctionAwardDocumentResource(BaseAuctionAwardDocumentResource):
    pass
