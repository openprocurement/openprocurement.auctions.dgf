# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.other.complaint import (
    AuctionComplaintResource,
)


@opresource(name='dgfFinancialAssets:Auction Complaints',
            collection_path='/auctions/{auction_id}/complaints',
            path='/auctions/{auction_id}/complaints/{complaint_id}',
            auctionsprocurementMethodType="dgfFinancialAssets",
            description="Financial auction complaints")
class FinancialAuctionComplaintResource(AuctionComplaintResource):
    pass
