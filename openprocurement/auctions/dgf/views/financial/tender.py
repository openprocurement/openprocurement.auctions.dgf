# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.other.tender import (
    AuctionResource,
)


@opresource(name='dgfFinancialAssets:Auction',
            path='/auctions/{auction_id}',
            auctionsprocurementMethodType="dgfFinancialAssets",
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#auction for more info")
class FinancialAuctionResource(AuctionResource):
    pass
