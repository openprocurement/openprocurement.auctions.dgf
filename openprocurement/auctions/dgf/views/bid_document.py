# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.auctions.core.utils import (
    get_file,
    save_auction,
    upload_file,
    apply_patch,
    update_file_content_type,
    opresource,

)
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,

)
from openprocurement.auctions.core.validation import (
    validate_patch_document_data,
)


@opresource(name='Auction Bid Documents',
            collection_path='/auctions/{auction_id}/bids/{bid_id}/documents',
            path='/auctions/{auction_id}/bids/{bid_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction bidder documents")
class AuctionBidDocumentResource(APIResource):

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Bid Documents List"""
        if self.request.validated['auction_status'] in ['active.tendering', 'active.auction'] and self.request.authenticated_role != 'bid_owner':
            self.request.errors.add('body', 'data', 'Can\'t view bid documents in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(validators=(validate_file_upload,), permission='edit_bid')
    def collection_post(self):
        """Auction Bid Document Upload
        """
        if self.request.validated['auction_status'] not in ['active.tendering', 'active.qualification']:
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        auction = self.request.validated['auction']
        if self.request.validated['auction_status'] == 'active.tendering' and (auction.tenderPeriod.startDate and get_now() < auction.tenderPeriod.startDate or get_now() > auction.tenderPeriod.endDate):
            self.request.errors.add('body', 'data', 'Document can be added only during the tendering period: from ({}) to ({}).'.format(auction.auctionPeriod.startDate and auction.auctionPeriod.startDate.isoformat(), auction.auctionPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        if self.request.validated['auction_status'] == 'active.qualification' and not [i for i in self.request.validated['auction'].awards if i.status == 'pending' and i.bid_id == self.request.validated['bid_id']]:
            self.request.errors.add('body', 'data', 'Can\'t add document because award of bid is not in pending state')
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.context.documents.append(document)
        if self.request.validated['auction_status'] == 'active.tendering':
            self.request.validated['auction'].modified = False
        if save_auction(self.request):
            self.LOGGER.info('Created auction bid document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_bid_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        """Auction Bid Document Read"""
        if self.request.validated['auction_status'] in ['active.tendering', 'active.auction'] and self.request.authenticated_role != 'bid_owner':
            self.request.errors.add('body', 'data', 'Can\'t view bid document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if self.request.params.get('download'):
            return get_file(self.request)
        document = self.request.validated['document']
        document_data = document.serialize("view")
        document_data['previousVersions'] = [
            i.serialize("view")
            for i in self.request.validated['documents']
            if i.url != document.url
        ]
        return {'data': document_data}

    @json_view(validators=(validate_file_update,), permission='edit_bid')
    def put(self):
        """Auction Bid Document Update"""
        if self.request.validated['auction_status'] not in ['active.tendering', 'active.qualification']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        auction = self.request.validated['auction']
        if self.request.validated['auction_status'] == 'active.tendering' and (auction.tenderPeriod.startDate and get_now() < auction.tenderPeriod.startDate or get_now() > auction.tenderPeriod.endDate):
            self.request.errors.add('body', 'data', 'Document can be updated only during the tendering period: from ({}) to ({}).'.format(auction.auctionPeriod.startDate and auction.auctionPeriod.startDate.isoformat(), auction.auctionPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        if self.request.validated['auction_status'] == 'active.qualification' and not [i for i in self.request.validated['auction'].awards if i.status == 'pending' and i.bid_id == self.request.validated['bid_id']]:
            self.request.errors.add('body', 'data', 'Can\'t update document because award of bid is not in pending state')
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.request.validated['bid'].documents.append(document)
        if self.request.validated['auction_status'] == 'active.tendering':
            self.request.validated['auction'].modified = False
        if save_auction(self.request):
            self.LOGGER.info('Updated auction bid document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_bid_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission='edit_bid')
    def patch(self):
        """Auction Bid Document Update"""
        if self.request.validated['auction_status'] not in ['active.tendering', 'active.qualification']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        auction = self.request.validated['auction']
        if self.request.validated['auction_status'] == 'active.tendering' and (auction.tenderPeriod.startDate and get_now() < auction.tenderPeriod.startDate or get_now() > auction.tenderPeriod.endDate):
            self.request.errors.add('body', 'data', 'Document can be updated only during the tendering period: from ({}) to ({}).'.format(auction.auctionPeriod.startDate and auction.auctionPeriod.startDate.isoformat(), auction.auctionPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        if self.request.validated['auction_status'] == 'active.qualification' and not [i for i in self.request.validated['auction'].awards if i.status == 'pending' and i.bid_id == self.request.validated['bid_id']]:
            self.request.errors.add('body', 'data', 'Can\'t update document because award of bid is not in pending state')
            self.request.errors.status = 403
            return
        if self.request.validated['auction_status'] == 'active.tendering':
            self.request.validated['auction'].modified = False
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated auction bid document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_bid_document_patch'}))
            return {'data': self.request.context.serialize("view")}
