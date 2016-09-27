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
    opresource,
)
from openprocurement.auctions.core.validation import (
    validate_lot_data,
    validate_patch_lot_data,
)


@opresource(name='dgfOtherAssets:Auction Lots',
            collection_path='/auctions/{auction_id}/lots',
            path='/auctions/{auction_id}/lots/{lot_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction lots")
class AuctionLotResource(APIResource):

    @json_view(content_type="application/json", validators=(validate_lot_data,), permission='edit_auction')
    def collection_post(self):
        """Add a lot
        """
        auction = self.request.validated['auction']
        if auction.status not in ['active.tendering']:
            self.request.errors.add('body', 'data', 'Can\'t add lot in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        lot = self.request.validated['lot']
        lot.date = get_now()
        auction.lots.append(lot)
        if save_auction(self.request):
            self.LOGGER.info('Created auction lot {}'.format(lot.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_lot_create'}, {'lot_id': lot.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=route, lot_id=lot.id, _query={})
            return {'data': lot.serialize("view")}

    @json_view(permission='view_auction')
    def collection_get(self):
        """Lots Listing
        """
        return {'data': [i.serialize("view") for i in self.request.validated['auction'].lots]}

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the lot
        """
        return {'data': self.request.context.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_lot_data,), permission='edit_auction')
    def patch(self):
        """Update of lot
        """
        auction = self.request.validated['auction']
        if auction.status not in ['active.tendering']:
            self.request.errors.add('body', 'data', 'Can\'t update lot in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            self.LOGGER.info('Updated auction lot {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_lot_patch'}))
            return {'data': self.request.context.serialize("view")}

    @json_view(permission='edit_auction')
    def delete(self):
        """Lot deleting
        """
        auction = self.request.validated['auction']
        if auction.status not in ['active.tendering']:
            self.request.errors.add('body', 'data', 'Can\'t delete lot in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        lot = self.request.context
        res = lot.serialize("view")
        auction.lots.remove(lot)
        if save_auction(self.request):
            self.LOGGER.info('Deleted auction lot {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_lot_delete'}))
            return {'data': res}
