# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    opresource
)
from openprocurement.auctions.core.plugins.awarding_2_0.views import (
    AuctionAwardComplaintResource as BaseAuctionAwardComplaintResource
)


@opresource(name='dgfOtherAssets:Auction Award Complaints',
            collection_path='/auctions/{auction_id}/awards/{award_id}/complaints',
            path='/auctions/{auction_id}/awards/{award_id}/complaints/{complaint_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction award complaints")
class AuctionAwardComplaintResource(BaseAuctionAwardComplaintResource):
    pass
