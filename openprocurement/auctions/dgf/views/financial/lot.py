# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.other.lot import (
    AuctionLotResource,
)


@opresource(name='Financial Auction Lots',
            collection_path='/auctions/{auction_id}/lots',
            path='/auctions/{auction_id}/lots/{lot_id}',
            auctionsprocurementMethodType="dgfFinancialAssets",
            description="Financial auction lots")
class FinancialAuctionLotResource(AuctionLotResource):
    pass
