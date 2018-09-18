# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    apply_patch,
    cleanup_bids_for_cancelled_lots,
    context_unpack,
    json_view,
    opresource,
    save_auction,
)
from openprocurement.auctions.core.validation import (
    validate_auction_auction_data,
)
from openprocurement.auctions.core.views.mixins import AuctionAuctionResource

from openprocurement.auctions.core.plugins.awarding.base.utils import invalidate_bids_under_threshold


@opresource(name='dgfOtherAssets:Auction Auction',
            collection_path='/auctions/{auction_id}/auction',
            path='/auctions/{auction_id}/auction/{auction_lot_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="auction auction data")
class AuctionAuctionResource(AuctionAuctionResource):

    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def collection_post(self):
        apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
        auction = self.request.validated['auction']
        invalidate_bids_under_threshold(auction)
        if any([i.status == 'active' for i in auction.bids]):
            self.request.content_configurator.start_awarding()
        else:
            auction.status = 'unsuccessful'
        if save_auction(self.request):
            self.LOGGER.info('Report auction results', extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_auction_post'}))
            return {'data': self.request.validated['auction'].serialize(self.request.validated['auction'].status)}

    @json_view(content_type="application/json", permission='auction', validators=(validate_auction_auction_data))
    def post(self):
        """Report auction results for lot.
        """
        apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
        auction = self.request.validated['auction']
        if all([i.auctionPeriod and i.auctionPeriod.endDate for i in auction.lots if i.numberOfBids > 1 and i.status == 'active']):
            cleanup_bids_for_cancelled_lots(auction)
            invalidate_bids_under_threshold(auction)
            if any([i.status == 'active' for i in auction.bids]):
                self.request.content_configurator.start_awarding()
            else:
                auction.status = 'unsuccessful'
        if save_auction(self.request):
            self.LOGGER.info('Report auction results', extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_lot_auction_post'}))
            return {'data': self.request.validated['auction'].serialize(self.request.validated['auction'].status)}
