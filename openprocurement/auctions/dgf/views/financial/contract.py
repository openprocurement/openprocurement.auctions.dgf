# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.other.contract import (
    AuctionAwardContractResource,
)


@opresource(name='dgfFinancialAssets:Auction Contracts',
            collection_path='/auctions/{auction_id}/contracts',
            path='/auctions/{auction_id}/contracts/{contract_id}',
            auctionsprocurementMethodType="dgfFinancialAssets",
            description=" Financial auction contracts")
class FinancialAuctionAwardContractResource(AuctionAwardContractResource):
    pass
