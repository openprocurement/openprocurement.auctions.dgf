# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.other.auction import (
    AuctionAuctionResource,
)


@opresource(name='dgfFinancialAssets:Auction Auction',
            collection_path='/auctions/{auction_id}/auction',
            path='/auctions/{auction_id}/auction/{auction_lot_id}',
            auctionsprocurementMethodType="dgfFinancialAssets",
            description="Financial auction auction data")
class FinancialAuctionAuctionResource(AuctionAuctionResource):
    pass
