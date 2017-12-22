# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.core.plugins.awarding_2_0.views import (
    AuctionAwardDocumentResource,
)


@opresource(name='dgfFinancialAssets:Auction Award Documents',
            collection_path='/auctions/{auction_id}/awards/{award_id}/documents',
            path='/auctions/{auction_id}/awards/{award_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfFinancialAssets",
            description="Financial auction award documents")
class FinancialAuctionAwardDocumentResource(AuctionAwardDocumentResource):
    pass
