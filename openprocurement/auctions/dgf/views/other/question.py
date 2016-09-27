# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    save_auction,
    opresource,

)
from openprocurement.auctions.core.validation import (
    validate_question_data,
    validate_patch_question_data,
)


@opresource(name='dgfOtherAssets:Auction Questions',
            collection_path='/auctions/{auction_id}/questions',
            path='/auctions/{auction_id}/questions/{question_id}',
            auctionsprocurementMethodType="dgfOtherAssets",
            description="Auction questions")
class AuctionQuestionResource(APIResource):

    @json_view(content_type="application/json", validators=(validate_question_data,), permission='create_question')
    def collection_post(self):
        """Post a question
        """
        auction = self.request.validated['auction']
        if auction.status != 'active.tendering' or get_now() < auction.enquiryPeriod.startDate or get_now() > auction.enquiryPeriod.endDate:
            self.request.errors.add('body', 'data', 'Can add question only in enquiryPeriod')
            self.request.errors.status = 403
            return
        question = self.request.validated['question']
        if any([i.status != 'active' for i in auction.lots if i.id == question.relatedItem]):
            self.request.errors.add('body', 'data', 'Can add question only in active lot status')
            self.request.errors.status = 403
            return
        auction.questions.append(question)
        if save_auction(self.request):
            self.LOGGER.info('Created auction question {}'.format(question.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_question_create'}, {'question_id': question.id}))
            self.request.response.status = 201
            route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=route, question_id=question.id, _query={})
            return {'data': question.serialize("view")}

    @json_view(permission='view_auction')
    def collection_get(self):
        """List questions
        """
        return {'data': [i.serialize(self.request.validated['auction'].status) for i in self.request.validated['auction'].questions]}

    @json_view(permission='view_auction')
    def get(self):
        """Retrieving the question
        """
        return {'data': self.request.validated['question'].serialize(self.request.validated['auction'].status)}

    @json_view(content_type="application/json", permission='edit_auction', validators=(validate_patch_question_data,))
    def patch(self):
        """Post an Answer
        """
        auction = self.request.validated['auction']
        if auction.status != 'active.tendering':
            self.request.errors.add('body', 'data', 'Can\'t update question in current ({}) auction status'.format(auction.status))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in auction.lots if i.id == self.request.context.relatedItem]):
            self.request.errors.add('body', 'data', 'Can update question only in active lot status')
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            self.LOGGER.info('Updated auction question {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_question_patch'}))
            return {'data': self.request.context.serialize(auction.status)}
