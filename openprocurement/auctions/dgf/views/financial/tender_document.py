# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.other.tender_document import (
    AuctionDocumentResource,
)


@opresource(name='Financial Auction Documents',
            collection_path='/auctions/{auction_id}/documents',
            path='/auctions/{auction_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfFinancialAssets",
            description="Financial auction related binary files (PDFs, etc.)")
class FinancialAuctionDocumentResource(AuctionDocumentResource):
    pass
