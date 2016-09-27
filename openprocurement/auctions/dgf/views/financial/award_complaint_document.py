# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.other.award_complaint_document import (
    AuctionAwardComplaintDocumentResource,
)


@opresource(name='dgfFinancialAssets:Auction Award Complaint Documents',
            collection_path='/auctions/{auction_id}/awards/{award_id}/complaints/{complaint_id}/documents',
            path='/auctions/{auction_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfFinancialAssets",
            description="Financial auction award complaint documents")
class FinancialAuctionAwardComplaintDocumentResource(AuctionAwardComplaintDocumentResource):
    pass