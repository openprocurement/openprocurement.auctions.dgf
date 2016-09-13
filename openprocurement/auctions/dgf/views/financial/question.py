# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.other.question import (
    AuctionQuestionResource,
)


@opresource(name='Financial Auction Questions',
            collection_path='/auctions/{auction_id}/questions',
            path='/auctions/{auction_id}/questions/{question_id}',
            auctionsprocurementMethodType="dgfFinancialAssets",
            description="Financial Auction questions")
class FinancialAuctionQuestionResource(AuctionQuestionResource):
    pass
