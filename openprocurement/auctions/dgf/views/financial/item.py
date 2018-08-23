# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import opresource
from openprocurement.auctions.core.endpoints import ENDPOINTS
from openprocurement.auctions.dgf.views.other.item import AuctionItemResource


@opresource(
    name='dgfFinancialAssets:Auction Items',
    collection_path=ENDPOINTS['items'],
    path=ENDPOINTS['item'],
    auctionsprocurementMethodType="dgfFinancialAssets",
    description="Auction items")
class AuctionItemResource(AuctionItemResource):
    pass
