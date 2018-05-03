# -*- coding: utf-8 -*-
from datetime import timedelta

from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from schematics.types import (
    StringType,
    IntType,
    DateType,
    MD5Type,
    BooleanType
)
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from urlparse import urlparse, parse_qs
from string import hexdigits
from zope.interface import implementer

from openprocurement.auctions.core.constants import (
    DGF_ELIGIBILITY_CRITERIA,
    DGF_PLATFORM_LEGAL_DETAILS,
    DGF_PLATFORM_LEGAL_DETAILS_FROM,
    DGF_ID_REQUIRED_FROM,
    DGF_DECISION_REQUIRED_FROM,
)
from openprocurement.auctions.core.includeme import IAwardingNextCheck
from openprocurement.auctions.core.models import (
    ListType,
    ComplaintModelType,
    IAuction,
    Auction as BaseAuction,
    Bid as BaseBid,
    dgfCancellation as Cancellation,
    dgfItem as Item,
    dgfDocument as Document,
    dgfComplaint as Complaint,
    Feature,
    Period,
    Lot,
    dgf_auction_roles,
    get_auction,
    validate_features_uniq,
    validate_lots_uniq,
    validate_items_uniq,
    calc_auction_end_time,
    validate_not_available,
    FinancialOrganization
)
from openprocurement.auctions.core.plugins.awarding.v3.models import (
    Award
)
from openprocurement.auctions.core.plugins.contracting.v3.models import (
    Contract,
)
from openprocurement.auctions.core.utils import (
    rounding_shouldStartAfter_after_midnigth,
    AUCTIONS_COMPLAINT_STAND_STILL_TIME,
    calculate_business_date,
    get_request_from_root,
    get_now,
    TZ
)
from openprocurement.auctions.core.validation import (
    validate_disallow_dgfPlatformLegalDetails
)


class Bid(BaseBid):
    class Options:
        roles = {
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'qualified'),
        }

    status = StringType(choices=['active', 'draft', 'invalid'], default='active')
    documents = ListType(ModelType(Document), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])
    qualified = BooleanType(required=True, choices=[True])


class AuctionAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        auction = self.__parent__
        if auction.lots or auction.status not in ['active.tendering', 'active.auction']:
            return
        if self.startDate and get_now() > calc_auction_end_time(auction.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(auction.numberOfBids, self.startDate)
        elif auction.tenderPeriod and auction.tenderPeriod.endDate:
            start_after = auction.tenderPeriod.endDate
        else:
            return
        return rounding_shouldStartAfter_after_midnigth(start_after, auction).isoformat()

    def validate_startDate(self, data, startDate):
        auction = get_auction(data['__parent__'])
        if not auction.revisions and not startDate:
            raise ValidationError(u'This field is required.')


class IDgfAuction(IAuction):
    """Marker interface for Dgf auctions"""


@implementer(IDgfAuction)
class Auction(BaseAuction):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    class Options:
        roles = dgf_auction_roles
    _procedure_type = "dgfOtherAssets"
    awards = ListType(ModelType(Award), default=list())
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the auction.
    cancellations = ListType(ModelType(Cancellation), default=list())
    complaints = ListType(ComplaintModelType(Complaint), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    dgfID = StringType()
    merchandisingObject = MD5Type()
    dgfDecisionID = StringType()
    dgfDecisionDate = DateType()
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the auction.
    enquiryPeriod = ModelType(Period)  # The period during which enquiries may be made and will be answered.
    tenderPeriod = ModelType(Period)  # The period when the auction is open for submissions. The end date is the closing date for auction submissions.
    tenderAttempts = IntType(choices=[1, 2, 3, 4, 5, 6, 7, 8])
    auctionPeriod = ModelType(AuctionAuctionPeriod, required=True, default={})
    status = StringType(choices=['draft', 'pending.verification', 'invalid', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')
    features = ListType(ModelType(Feature), validators=[validate_features_uniq, validate_not_available])
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq, validate_not_available])
    items = ListType(ModelType(Item), default=list(), validators=[validate_items_uniq])
    suspended = BooleanType()

    def __acl__(self):
        return [
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_auction'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_auction_award'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_auction_documents'),
        ]

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == 'Administrator':
            role = 'Administrator'
        elif request.authenticated_role == 'chronograph':
            role = 'chronograph'
        elif request.authenticated_role == 'auction':
            role = 'auction_{}'.format(request.method.lower())
        elif request.authenticated_role == 'convoy':
            role = 'convoy'
        else:
            role = 'edit_{}'.format(request.context.status)
        return role

    def initialize(self):
        if not self.enquiryPeriod:
            self.enquiryPeriod = type(self).enquiryPeriod.model_class()
        if not self.tenderPeriod:
            self.tenderPeriod = type(self).tenderPeriod.model_class()
        now = get_now()
        start_date = TZ.localize(self.auctionPeriod.startDate.replace(tzinfo=None))
        self.auctionPeriod.startDate = None
        self.auctionPeriod.endDate = None
        self.tenderPeriod.startDate = self.enquiryPeriod.startDate = now
        pause_between_periods = start_date - (start_date.replace(hour=20, minute=0, second=0, microsecond=0) - timedelta(days=1))
        end_date = calculate_business_date(start_date, -pause_between_periods, self)
        self.enquiryPeriod.endDate = end_date
        self.tenderPeriod.endDate = self.enquiryPeriod.endDate
        self.date = now
        if self.lots:
            for lot in self.lots:
                lot.date = now
        self.documents.append(type(self).documents.model_class(DGF_PLATFORM_LEGAL_DETAILS))

    def validate_documents(self, data, docs):
        if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_PLATFORM_LEGAL_DETAILS_FROM and \
                (docs and docs[0].documentType != 'x_dgfPlatformLegalDetails' or any([i.documentType == 'x_dgfPlatformLegalDetails' for i in docs[1:]])):
            raise ValidationError(u"First document should be document with x_dgfPlatformLegalDetails documentType")

    def validate_value(self, data, value):
        if value.currency != u'UAH':
            raise ValidationError(u"currency should be only UAH")

    def validate_dgfID(self, data, dgfID):
        if not dgfID and data['status'] not in ['draft', 'pending.verification', 'invalid']:
            if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_ID_REQUIRED_FROM:
                raise ValidationError(u'This field is required.')

    def validate_dgfDecisionID(self, data, dgfDecisionID):
        if not dgfDecisionID:
            if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_DECISION_REQUIRED_FROM:
                raise ValidationError(u'This field is required.')

    def validate_dgfDecisionDate(self, data, dgfDecisionDate):
        if not dgfDecisionDate:
            if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_DECISION_REQUIRED_FROM:
                raise ValidationError(u'This field is required.')

    def validate_merchandisingObject(self, data, merchandisingObject):
        if data['status'] == 'pending.verification' and not merchandisingObject:
            raise ValidationError(u'This field is required.')

    def validate_items(self, data, items):
        if data['status'] not in ['draft', 'pending.verification', 'invalid']:
            if not items:
                raise ValidationError(u'This field is required.')
            elif len(items) < 1:
                raise ValidationError(u'Please provide at least 1 item.')


    @serializable(serialize_when_none=False)
    def next_check(self):
        if self.suspended:
            return None
        now = get_now()
        checks = []
        if self.status == 'active.tendering' and self.tenderPeriod and self.tenderPeriod.endDate:
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))
        elif not self.lots and self.status == 'active.auction' and self.auctionPeriod and self.auctionPeriod.startDate and not self.auctionPeriod.endDate:
            if now < self.auctionPeriod.startDate:
                checks.append(self.auctionPeriod.startDate.astimezone(TZ))
            elif now < calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ):
                checks.append(calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ))
        elif self.lots and self.status == 'active.auction':
            for lot in self.lots:
                if lot.status != 'active' or not lot.auctionPeriod or not lot.auctionPeriod.startDate or lot.auctionPeriod.endDate:
                    continue
                if now < lot.auctionPeriod.startDate:
                    checks.append(lot.auctionPeriod.startDate.astimezone(TZ))
                elif now < calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ):
                    checks.append(calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ))
        # Use next_check part from awarding 2.0
        request = get_request_from_root(self)
        if request is not None:
            awarding_check = request.registry.getAdapter(self, IAwardingNextCheck).add_awarding_checks(self)
            if awarding_check is not None:
                checks.append(awarding_check)
        if self.status.startswith('active'):
            from openprocurement.auctions.core.utils import calculate_business_date
            for complaint in self.complaints:
                if complaint.status == 'claim' and complaint.dateSubmitted:
                    checks.append(calculate_business_date(complaint.dateSubmitted, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
                elif complaint.status == 'answered' and complaint.dateAnswered:
                    checks.append(calculate_business_date(complaint.dateAnswered, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
            for award in self.awards:
                for complaint in award.complaints:
                    if complaint.status == 'claim' and complaint.dateSubmitted:
                        checks.append(calculate_business_date(complaint.dateSubmitted, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
                    elif complaint.status == 'answered' and complaint.dateAnswered:
                        checks.append(calculate_business_date(complaint.dateAnswered, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
        return min(checks).isoformat() if checks else None


DGFOtherAssets = Auction

# DGF Financial Assets models


class Bid(Bid):
    class Options:
        roles = {
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'qualified', 'eligible'),
        }
    documents = ListType(ModelType(Document), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])
    tenderers = ListType(ModelType(FinancialOrganization), required=True, min_size=1, max_size=1)
    eligible = BooleanType(required=True, choices=[True])


@implementer(IAuction)
class Auction(DGFOtherAssets):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    _procedure_type = "dgfFinancialAssets"
    bids = ListType(ModelType(Bid), default=list())
    eligibilityCriteria = StringType(default=DGF_ELIGIBILITY_CRITERIA['ua'])
    eligibilityCriteria_en = StringType(default=DGF_ELIGIBILITY_CRITERIA['en'])
    eligibilityCriteria_ru = StringType(default=DGF_ELIGIBILITY_CRITERIA['ru'])


DGFFinancialAssets = Auction
