# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
    get_now
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    save_auction,
    add_next_award,
    opresource,

)
from openprocurement.auctions.core.validation import (
    validate_cancellation_data,
    validate_patch_cancellation_data,
)


@opresource(name='dgfOtherAssets:Auction Cancellations',
            collection_path='/auctions/{auction_id}/cancellations',
            path='/auctions/{auction_id}/cancellations/{cancellation_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction cancellations")
class AuctionCancellationResource(APIResource):

    def cancel_auction(self):
        auction = self.request.validated['auction']
        if auction.status in ['active.tendering', 'active.auction']:
            auction.bids = []
        auction.status = 'cancelled'

    def cancel_lot(self, cancellation=None):

        if not cancellation:
            cancellation = self.context
        auction = self.request.validated['auction']
        [setattr(i, 'status', 'cancelled') for i in auction.lots if i.id == cancellation.relatedLot]
        statuses = set([lot.status for lot in auction.lots])
        if statuses == set(['cancelled']):
            self.cancel_auction()
        elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
            auction.status = 'unsuccessful'
        elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
            auction.status = 'complete'
        if auction.status == 'active.auction' and all([
            i.auctionPeriod and i.auctionPeriod.endDate
            for i in self.request.validated['auction'].lots
            if i.numberOfBids > 1 and i.status == 'active'
        ]):
            add_next_award(self.request)

    @json_view(content_type="application/json", validators=(validate_cancellation_data,), permission='edit_auction')
    def collection_post(self):
        """Post a cancellation
        """
        auction = self.request.validated['auction']
        if auction.status in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t add cancellation in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        cancellation = self.request.validated['cancellation']
        cancellation.date = get_now()
        if any([i.status != 'active' for i in auction.lots if i.id == cancellation.relatedLot]):
            self.request.errors.add('body', 'data', 'Can add cancellation only in active lot status')
            self.request.errors.status = 403
            return
        if cancellation.relatedLot and cancellation.status == 'active':
            self.cancel_lot(cancellation)
        elif cancellation.status == 'active':
            self.cancel_auction()
        auction.cancellations.append(cancellation)
        if save_auction(self.request):
            self.LOGGER.info('Created auction cancellation {}'.format(cancellation.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_cancellation_create'}, {'cancellation_id': cancellation.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=route, cancellation_id=cancellation.id, _query={})
            return {'data': cancellation.serialize("view")}

    @json_view(permission='view_auction')
    def collection_get(self):
        """List cancellations
        """
        return {'data': [i.serialize("view") for i in self.request.validated['auction'].cancellations]}

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the cancellation
        """
        return {'data': self.request.validated['cancellation'].serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_cancellation_data,), permission='edit_auction')
    def patch(self):
        """Post a cancellation resolution
        """
        auction = self.request.validated['auction']
        if auction.status in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t update cancellation in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in auction.lots if i.id == self.request.context.relatedLot]):
            self.request.errors.add('body', 'data', 'Can update cancellation only in active lot status')
            self.request.errors.status = 403
            return
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if self.request.context.relatedLot and self.request.context.status == 'active':
            self.cancel_lot()
        elif self.request.context.status == 'active':
            self.cancel_auction()
        if save_auction(self.request):
            self.LOGGER.info('Updated auction cancellation {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_cancellation_patch'}))
            return {'data': self.request.context.serialize("view")}
