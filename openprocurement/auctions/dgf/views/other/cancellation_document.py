# -*- coding: utf-8 -*-
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
from openprocurement.auctions.core.utils import (
    save_auction,
    apply_patch,
    opresource,
)


@opresource(name='dgfOtherAssets:Auction Cancellation Documents',
            collection_path='/auctions/{auction_id}/cancellations/{cancellation_id}/documents',
            path='/auctions/{auction_id}/cancellations/{cancellation_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction cancellation documents")
class AuctionCancellationDocumentResource(APIResource):

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Cancellation Documents List"""
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(validators=(validate_file_upload,), permission='edit_auction')
    def collection_post(self):
        """Auction Cancellation Document Upload
        """
        if self.request.validated['auction_status'] in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Created auction cancellation document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_cancellation_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        """Auction Cancellation Document Read"""
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

    @json_view(validators=(validate_file_update,), permission='edit_auction')
    def put(self):
        """Auction Cancellation Document Update"""
        if self.request.validated['auction_status'] in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.request.validated['cancellation'].documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction cancellation document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_cancellation_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission='edit_auction')
    def patch(self):
        """Auction Cancellation Document Update"""
        if self.request.validated['auction_status'] in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated auction cancellation document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_cancellation_document_patch'}))
            return {'data': self.request.context.serialize("view")}
