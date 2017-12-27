# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import opresource
from openprocurement.auctions.core.contracting.dgf.views.contract import (
    BaseAuctionAwardContractResource
)


@opresource(name='dgfOtherAssets:Auction Contracts',
            collection_path='/auctions/{auction_id}/contracts',
            path='/auctions/{auction_id}/contracts/{contract_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction contracts")
class AuctionAwardContractResource(BaseAuctionAwardContractResource):
    pass
