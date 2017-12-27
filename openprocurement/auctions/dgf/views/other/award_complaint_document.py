# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.core.plugins.awarding_2_0.views.award_complaint_document import (
   AuctionAwardComplaintDocumentResource as BaseAuctionAwardComplaintDocumentResource
)


@opresource(name='dgfOtherAssets:Auction Award Complaint Documents',
            collection_path='/auctions/{auction_id}/awards/{award_id}/complaints/{complaint_id}/documents',
            path='/auctions/{auction_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction award complaint documents")
class AuctionAwardComplaintDocumentResource(BaseAuctionAwardComplaintDocumentResource):
    pass
