# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.utils import (
    context_unpack,
    json_view,
    set_ownership,
    APIResource,
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    check_auction_status,
    opresource,
    save_auction,

)
from openprocurement.auctions.core.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
)


@opresource(name='dgfOtherAssets:Auction Complaints',
            collection_path='/auctions/{auction_id}/complaints',
            path='/auctions/{auction_id}/complaints/{complaint_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction complaints")
class AuctionComplaintResource(APIResource):

    @json_view(content_type="application/json", validators=(validate_complaint_data,), permission='nobody')
    def collection_post(self):
        """Post a complaint
        """
        auction = self.context
        if auction.status not in ['active.tendering']:
            self.request.errors.add('body', 'data', 'Can\'t add complaint in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        complaint = self.request.validated['complaint']
        complaint.date = get_now()
        if complaint.status == 'claim':
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = 'draft'
        complaint.complaintID = '{}.{}{}'.format(auction.auctionID, self.server_id, sum([len(i.complaints) for i in auction.awards], len(auction.complaints)) + 1)
        set_ownership(complaint, self.request)
        auction.complaints.append(complaint)
        if save_auction(self.request):
            self.LOGGER.info('Created auction complaint {}'.format(complaint.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_complaint_create'}, {'complaint_id': complaint.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=route, complaint_id=complaint.id, _query={})
            return {
                'data': complaint.serialize(auction.status),
                'access': {
                    'token': complaint.owner_token
                }
            }

    @json_view(permission='view_auction')
    def collection_get(self):
        """List complaints
        """
        return {'data': [i.serialize("view") for i in self.context.complaints]}

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the complaint
        """
        return {'data': self.context.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_complaint_data,), permission='edit_complaint')
    def patch(self):
        """Post a complaint resolution
        """
        auction = self.request.validated['auction']
        if auction.status not in ['active.tendering', 'active.auction', 'active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t update complaint in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        if self.context.status not in ['draft', 'claim', 'answered', 'pending']:
            self.request.errors.add('body', 'data', 'Can\'t update complaint in current ({}) status'.format(self.context.status))
            self.request.errors.status = 403
            return
        data = self.request.validated['data']
        # complaint_owner
        if self.request.authenticated_role == 'complaint_owner' and self.context.status in ['draft', 'claim', 'answered', 'pending'] and data.get('status', self.context.status) == 'cancelled':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and auction.status in ['active.tendering'] and self.context.status == 'draft' and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'complaint_owner' and auction.status in ['active.tendering'] and self.context.status == 'draft' and data.get('status', self.context.status) == 'claim':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateSubmitted = get_now()
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status == 'answered' and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status == 'answered' and data.get('satisfied', self.context.satisfied) is True and data.get('status', self.context.status) == 'resolved':
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'complaint_owner' and self.context.status == 'answered' and data.get('satisfied', self.context.satisfied) is False and data.get('status', self.context.status) == 'pending':
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.type = 'complaint'
            self.context.dateEscalated = get_now()
        elif self.request.authenticated_role == 'auction_owner' and self.context.status == 'claim' and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'auction_owner' and self.context.status == 'claim' and data.get('resolution', self.context.resolution) and data.get('resolutionType', self.context.resolutionType) and data.get('status', self.context.status) == 'answered':
            if len(data.get('resolution', self.context.resolution)) < 20:
                self.request.errors.add('body', 'data', 'Can\'t update complaint: resolution too short')
                self.request.errors.status = 403
                return
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateAnswered = get_now()
        elif self.request.authenticated_role == 'auction_owner' and self.context.status == 'pending':
            apply_patch(self.request, save=False, src=self.context.serialize())
        # reviewers
        elif self.request.authenticated_role == 'reviewers' and self.context.status == 'pending' and data.get('status', self.context.status) == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif self.request.authenticated_role == 'reviewers' and self.context.status == 'pending' and data.get('status', self.context.status) in ['resolved', 'invalid', 'declined']:
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
        else:
            self.request.errors.add('body', 'data', 'Can\'t update complaint')
            self.request.errors.status = 403
            return
        if self.context.tendererAction and not self.context.tendererActionDate:
            self.context.tendererActionDate = get_now()
        if self.context.status not in ['draft', 'claim', 'answered', 'pending'] and auction.status in ['active.qualification', 'active.awarded']:
            check_auction_status(self.request)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction complaint {}'.format(self.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_complaint_patch'}))
            return {'data': self.context.serialize("view")}
