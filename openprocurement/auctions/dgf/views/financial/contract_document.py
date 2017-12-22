# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.core.contracting.dgf.views.\
    contract_document import BaseAuctionAwardContractDocumentResource


@opresource(name='dgfFinancialAssets:Auction Contract Documents',
            collection_path='/auctions/{auction_id}/contracts/{contract_id}/documents',
            path='/auctions/{auction_id}/contracts/{contract_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfFinancialAssets",
            description="Financial auction contract documents")
class FinancialAuctionAwardContractDocumentResource(
    BaseAuctionAwardContractDocumentResource
):
    pass
