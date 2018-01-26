# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, time
from schematics.types import (
    StringType,
    IntType,
    DateType
)
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types.serializable import serializable
from zope.interface import implementer
from pyramid.security import Allow
from openprocurement.api.interfaces import IAwardingNextCheck
from openprocurement.api.models import (
    BooleanType,
    ListType,
    Feature,
    Period,
    get_now,
    TZ,
    validate_features_uniq,
    validate_lots_uniq,
    validate_items_uniq,
    schematics_embedded_role,
    SANDBOX_MODE
)
from openprocurement.api.utils import (
    calculate_business_date,
    get_request_from_root
)
from openprocurement.auctions.core.models import (
    IAuction,
    dgfOrganization as Organization,
    Identifier,
    dgfItem as Item,
    dgfDocument as Document,
    dgfComplaint as Complaint
)
from openprocurement.auctions.core.plugins.awarding.v3.models import (
    Award
)
from openprocurement.auctions.core.plugins.awarding.v3.utils import (
    next_check_awarding
)
from openprocurement.auctions.core.plugins.contracting.v3.models import (
    Contract,
)
from openprocurement.auctions.core.validation import (
    validate_disallow_dgfPlatformLegalDetails
)
from openprocurement.auctions.flash.models import (
    Auction as BaseAuction,
    Bid as BaseBid,
    Cancellation as BaseCancellation,
    Lot,
    edit_role,
    calc_auction_end_time,
    COMPLAINT_STAND_STILL_TIME,
    Organization as BaseOrganization,
    ProcuringEntity as BaseProcuringEntity,
    Question as BaseQuestion,
    get_auction,
    Administrator_role
)

from .constants import (
    ELIGIBILITY_CRITERIA,
    DGF_ID_REQUIRED_FROM,
    DGF_DECISION_REQUIRED_FROM,
    DGF_PLATFORM_LEGAL_DETAILS,
    DGF_PLATFORM_LEGAL_DETAILS_FROM
)


class ProcuringEntity(BaseProcuringEntity):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))


class Bid(BaseBid):
    class Options:
        roles = {
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'qualified'),
        }

    status = StringType(choices=['active', 'draft', 'invalid'], default='active')
    tenderers = ListType(ModelType(Organization), required=True, min_size=1, max_size=1)
    documents = ListType(ModelType(Document), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])
    qualified = BooleanType(required=True, choices=[True])


class Question(BaseQuestion):
    author = ModelType(Organization, required=True)


class Cancellation(BaseCancellation):
    documents = ListType(ModelType(Document), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])


def validate_not_available(items, *args):
    if items:
        raise ValidationError(u"Option not available in this procurementMethodType")


def rounding_shouldStartAfter(start_after, auction, use_from=datetime(2016, 6, 1, tzinfo=TZ)):
    if (auction.enquiryPeriod and auction.enquiryPeriod.startDate or get_now()) > use_from and not (SANDBOX_MODE and auction.submissionMethodDetails and u'quick' in auction.submissionMethodDetails):
        midnigth = datetime.combine(start_after.date(), time(0, tzinfo=start_after.tzinfo))
        if start_after >= midnigth:
            start_after = midnigth + timedelta(1)
    return start_after


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
        return rounding_shouldStartAfter(start_after, auction).isoformat()

    def validate_startDate(self, data, startDate):
        auction = get_auction(data['__parent__'])
        if not auction.revisions and not startDate:
            raise ValidationError(u'This field is required.')


create_role = (schematics_embedded_role + blacklist('owner_token', 'owner', '_attachments', 'revisions', 'date', 'dateModified', 'doc_id', 'auctionID', 'bids', 'documents', 'awards', 'questions', 'complaints', 'auctionUrl', 'status', 'enquiryPeriod', 'tenderPeriod', 'awardPeriod', 'procurementMethod', 'eligibilityCriteria', 'eligibilityCriteria_en', 'eligibilityCriteria_ru', 'awardCriteria', 'submissionMethod', 'cancellations', 'numberOfBidders', 'contracts', 'suspended'))
edit_role = (edit_role + blacklist('enquiryPeriod', 'tenderPeriod', 'value', 'auction_value', 'minimalStep', 'auction_minimalStep', 'guarantee', 'auction_guarantee', 'eligibilityCriteria', 'eligibilityCriteria_en', 'eligibilityCriteria_ru', 'awardCriteriaDetails', 'awardCriteriaDetails_en', 'awardCriteriaDetails_ru', 'procurementMethodRationale', 'procurementMethodRationale_en', 'procurementMethodRationale_ru', 'submissionMethodDetails', 'submissionMethodDetails_en', 'submissionMethodDetails_ru', 'items', 'procuringEntity', 'suspended'))
Administrator_role = (whitelist('suspended', 'awards') + Administrator_role)


class IDgfAuction(IAuction):
    """Marker interface for Dgf auctions"""


@implementer(IDgfAuction)
class Auction(BaseAuction):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    class Options:
        roles = {
            'create': create_role,
            'edit_active.tendering': edit_role,
            'Administrator': Administrator_role,
        }

    awards = ListType(ModelType(Award), default=list())
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the auction.
    cancellations = ListType(ModelType(Cancellation), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    dgfID = StringType()
    dgfDecisionID = StringType()
    dgfDecisionDate = DateType()
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the auction.
    enquiryPeriod = ModelType(Period)  # The period during which enquiries may be made and will be answered.
    tenderPeriod = ModelType(Period)  # The period when the auction is open for submissions. The end date is the closing date for auction submissions.
    tenderAttempts = IntType(choices=[1, 2, 3, 4, 5, 6, 7, 8])
    auctionPeriod = ModelType(AuctionAuctionPeriod, required=True, default={})
    procurementMethodType = StringType(default="dgfOtherAssets")
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(choices=['draft', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')
    questions = ListType(ModelType(Question), default=list())
    features = ListType(ModelType(Feature), validators=[validate_features_uniq, validate_not_available])
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq, validate_not_available])
    items = ListType(ModelType(Item), required=True, min_size=1, validators=[validate_items_uniq])
    suspended = BooleanType()

    def __acl__(self):
        return [
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_auction'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_auction_award'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_auction_documents'),
        ]

    def initialize(self):
        if not self.enquiryPeriod:
            self.enquiryPeriod = type(self).enquiryPeriod.model_class()
        if not self.tenderPeriod:
            self.tenderPeriod = type(self).tenderPeriod.model_class()
        now = get_now()
        self.tenderPeriod.startDate = self.enquiryPeriod.startDate = now
        pause_between_periods = self.auctionPeriod.startDate - (self.auctionPeriod.startDate.replace(hour=20, minute=0, second=0, microsecond=0) - timedelta(days=1))
        self.enquiryPeriod.endDate = self.tenderPeriod.endDate = calculate_business_date(self.auctionPeriod.startDate, -pause_between_periods, self)
        self.auctionPeriod.startDate = None
        self.auctionPeriod.endDate = None
        self.date = now
        if self.lots:
            for lot in self.lots:
                lot.date = now
        self.documents.append(type(self).documents.model_class(DGF_PLATFORM_LEGAL_DETAILS))

    def validate_documents(self, data, docs):
        if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_PLATFORM_LEGAL_DETAILS_FROM and \
                (docs and docs[0].documentType != 'x_dgfPlatformLegalDetails' or any([i.documentType == 'x_dgfPlatformLegalDetails' for i in docs[1:]])):
            raise ValidationError(u"First document should be document with x_dgfPlatformLegalDetails documentType")

    def validate_tenderPeriod(self, data, period):
        pass

    def validate_value(self, data, value):
        if value.currency != u'UAH':
            raise ValidationError(u"currency should be only UAH")

    def validate_dgfID(self, data, dgfID):
        if not dgfID:
            if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_ID_REQUIRED_FROM:
                raise ValidationError(u'This field is required.')

    def validate_dgfDecisionID(self, data, dgfID):
        if not dgfID:
            if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_DECISION_REQUIRED_FROM:
                raise ValidationError(u'This field is required.')

    def validate_dgfDecisionDate(self, data, dgfID):
        if not dgfID:
            if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_DECISION_REQUIRED_FROM:
                raise ValidationError(u'This field is required.')

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
            from openprocurement.api.utils import calculate_business_date
            for complaint in self.complaints:
                if complaint.status == 'claim' and complaint.dateSubmitted:
                    checks.append(calculate_business_date(complaint.dateSubmitted, COMPLAINT_STAND_STILL_TIME, self))
                elif complaint.status == 'answered' and complaint.dateAnswered:
                    checks.append(calculate_business_date(complaint.dateAnswered, COMPLAINT_STAND_STILL_TIME, self))
            for award in self.awards:
                for complaint in award.complaints:
                    if complaint.status == 'claim' and complaint.dateSubmitted:
                        checks.append(calculate_business_date(complaint.dateSubmitted, COMPLAINT_STAND_STILL_TIME, self))
                    elif complaint.status == 'answered' and complaint.dateAnswered:
                        checks.append(calculate_business_date(complaint.dateAnswered, COMPLAINT_STAND_STILL_TIME, self))
        return min(checks).isoformat() if checks else None


DGFOtherAssets = Auction

# DGF Financial Assets models


def validate_ua_fin(items, *args):
    if items and not any([i.scheme == u"UA-FIN" for i in items]):
        raise ValidationError(u"One of additional classifications should be UA-FIN.")


class FinantialOrganization(BaseOrganization):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier), required=True, validators=[validate_ua_fin])


class Document(Document):
    documentType = StringType(choices=[
        'auctionNotice', 'awardNotice', 'contractNotice',
        'notice', 'biddingDocuments', 'technicalSpecifications',
        'evaluationCriteria', 'clarifications', 'shortlistedFirms',
        'riskProvisions', 'billOfQuantity', 'bidders', 'conflictOfInterest',
        'debarments', 'evaluationReports', 'winningBid', 'complaints',
        'contractSigned', 'contractArrangements', 'contractSchedule',
        'contractAnnexe', 'contractGuarantees', 'subContract',
        'eligibilityCriteria', 'contractProforma', 'commercialProposal',
        'qualificationDocuments', 'eligibilityDocuments', 'tenderNotice',
        'illustration', 'financialLicense', 'virtualDataRoom',
        'auctionProtocol', 'x_dgfPublicAssetCertificate',
        'x_presentation', 'x_nda', 'x_dgfAssetFamiliarization',
        'x_dgfPlatformLegalDetails',
    ])


class Bid(Bid):
    class Options:
        roles = {
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'qualified', 'eligible'),
        }
    documents = ListType(ModelType(Document), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])
    tenderers = ListType(ModelType(FinantialOrganization), required=True, min_size=1, max_size=1)
    eligible = BooleanType(required=True, choices=[True])


@implementer(IAuction)
class Auction(DGFOtherAssets):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the auction.
    bids = ListType(ModelType(Bid), default=list())
    procurementMethodType = StringType(default="dgfFinancialAssets")
    eligibilityCriteria = StringType(default=ELIGIBILITY_CRITERIA['ua'])
    eligibilityCriteria_en = StringType(default=ELIGIBILITY_CRITERIA['en'])
    eligibilityCriteria_ru = StringType(default=ELIGIBILITY_CRITERIA['ru'])


DGFFinancialAssets = Auction
