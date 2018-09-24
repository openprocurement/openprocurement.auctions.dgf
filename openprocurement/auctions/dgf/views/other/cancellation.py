# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import opresource
from openprocurement.auctions.core.views.mixins import AuctionCancellationResource
from openprocurement.auctions.core.interfaces import IAuctionManager


@opresource(name='dgfOtherAssets:Auction Cancellations',
            collection_path='/auctions/{auction_id}/cancellations',
            path='/auctions/{auction_id}/cancellations/{cancellation_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction cancellations")
class AuctionCancellationResource(AuctionCancellationResource):

    def cancel_lot(self, cancellation=None):

        if not cancellation:
            cancellation = self.context
        auction = self.request.validated['auction']
        adapter = self.request.registry.getAdapter(auction, IAuctionManager)
        [setattr(i, 'status', 'cancelled') for i in auction.lots if i.id == cancellation.relatedLot]
        statuses = set([lot.status for lot in auction.lots])
        if statuses == set(['cancelled']):
            self.cancel_auction()
        elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
            adapter.pendify_auction_status('unsuccessful')
        elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
            adapter.pendify_auction_status('complete')
        if auction.status == 'active.auction' and all([
            i.auctionPeriod and i.auctionPeriod.endDate
            for i in self.request.validated['auction'].lots
            if i.numberOfBids > 1 and i.status == 'active'
        ]):
            self.request.content_configurator.start_awarding()
