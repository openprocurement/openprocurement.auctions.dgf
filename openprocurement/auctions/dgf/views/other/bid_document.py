# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.utils import (
    get_file,
    upload_file,
    update_file_content_type,
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)
from openprocurement.auctions.core.constants import (
    PROCEDURE_STATUSES,
)
from openprocurement.auctions.core.utils import (
    save_auction,
    apply_patch,
    opresource,
)


@opresource(name='dgfOtherAssets:Auction Bid Documents',
            collection_path='/auctions/{auction_id}/bids/{bid_id}/documents',
            path='/auctions/{auction_id}/bids/{bid_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction bidder documents")
class AuctionBidDocumentResource(APIResource):

    def validate_bid_document(self, operation):
        auction = self.request.validated['auction']
        if self.request.validated['auction_status'] not in PROCEDURE_STATUSES[auction.procurementMethodType]['bid_doc_interaction_statuses']:
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) auction status'.format(operation, auction.status))
            self.request.errors.status = 403
            return
        if auction.status in PROCEDURE_STATUSES[auction.procurementMethodType]['tender_period_statuses'] and not (auction.tenderPeriod.startDate < get_now() < auction.tenderPeriod.endDate):
            self.request.errors.add('body', 'data', 'Document can be {} only during the tendering period: from ({}) to ({}).'.format('added' if operation == 'add' else 'updated', auction.tenderPeriod.startDate.isoformat(), auction.tenderPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        if auction.status == 'active.qualification' and not [i for i in auction.awards if i.status == 'pending' and i.bid_id == self.request.validated['bid_id']]:
            self.request.errors.add('body', 'data', 'Can\'t {} document because award of bid is not in pending state'.format(operation))
            self.request.errors.status = 403
            return
        return True

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Bid Documents List"""
        auction = self.request.validated['auction']
        if self.request.validated['auction_status'] in PROCEDURE_STATUSES[auction.procurementMethodType]['bid_doc_interaction_statuses'] and self.request.authenticated_role != 'bid_owner':
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
        if not self.validate_bid_document('add'):
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
        auction = self.request.validated['auction']
        if self.request.validated['auction_status'] in PROCEDURE_STATUSES[auction.procurementMethodType]['tender_period_statuses'] and self.request.authenticated_role != 'bid_owner':
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
        if not self.validate_bid_document('update'):
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
        if not self.validate_bid_document('update'):
            return
        if self.request.validated['auction_status'] == 'active.tendering':
            self.request.validated['auction'].modified = False
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated auction bid document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_bid_document_patch'}))
            return {'data': self.request.context.serialize("view")}
