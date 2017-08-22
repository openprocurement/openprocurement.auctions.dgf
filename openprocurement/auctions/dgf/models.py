# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, time
from schematics.types import StringType, URLType, IntType, DateType, MD5Type
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types.serializable import serializable
from urlparse import urlparse, parse_qs
from string import hexdigits
from zope.interface import implementer
from pyramid.security import Allow
from openprocurement.api.models import (
    BooleanType, ListType, Feature, Period, get_now, TZ, ComplaintModelType,
    validate_features_uniq, validate_lots_uniq, Identifier as BaseIdentifier,
    Classification, validate_items_uniq, ORA_CODES, Address, Location,
    schematics_embedded_role, SANDBOX_MODE,
)
from openprocurement.api.utils import calculate_business_date
from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.flash.models import (
    Auction as BaseAuction, Document as BaseDocument, Bid as BaseBid,
    Complaint as BaseComplaint, Cancellation as BaseCancellation,
    Contract as BaseContract, Award as BaseAward, Lot, edit_role,
    calc_auction_end_time, COMPLAINT_STAND_STILL_TIME,
    Organization as BaseOrganization, Item as BaseItem,
    ProcuringEntity as BaseProcuringEntity, Question as BaseQuestion,
    get_auction, Administrator_role, view_role, enquiries_role
)
from schematics_flexible.schematics_flexible import FlexibleModelType
from openprocurement.schemas.dgf.schemas_store import SchemaStore


def read_json(name):
    import os.path
    from json import loads
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(curr_dir, name)
    with open(file_path) as lang_file:
        data = lang_file.read()
    return loads(data)


CAV_CODES = read_json('cav.json')
ORA_CODES = ORA_CODES[:]
ORA_CODES[0:0] = ["UA-IPN", "UA-FIN"]
DOCUMENT_TYPE_URL_ONLY = ['virtualDataRoom', 'x_dgfPublicAssetCertificate', 'x_dgfPlatformLegalDetails']
DOCUMENT_TYPE_OFFLINE = ['x_dgfAssetFamiliarization']
DGF_PLATFORM_LEGAL_DETAILS = {
    'url': 'http://torgi.fg.gov.ua/prozorrosale',
    'title': u'Місце та форма прийому заяв на участь в аукціоні та банківські реквізити для зарахування гарантійних внесків',
    'documentType': 'x_dgfPlatformLegalDetails',
}
DGF_PLATFORM_LEGAL_DETAILS_FROM = datetime(2016, 12, 23, tzinfo=TZ)

DGF_ID_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)
DGF_DECISION_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)


def validate_disallow_dgfPlatformLegalDetails(docs, *args):
    if any([i.documentType == 'x_dgfPlatformLegalDetails' for i in docs]):
        raise ValidationError(u"Disallow documents with x_dgfPlatformLegalDetails documentType")

VERIFY_AUCTION_PROTOCOL_TIME = timedelta(days=4)
AWARD_PAYMENT_TIME = timedelta(days=20)
CONTRACT_SIGNING_TIME = timedelta(days=20)


class CAVClassification(Classification):
    scheme = StringType(required=True, default=u'CAV', choices=[u'CAV'])
    id = StringType(required=True, choices=CAV_CODES)


class Item(BaseItem):
    """A good, service, or work to be contracted."""
    class Options:
        roles = {
            'create': blacklist('deliveryLocation', 'deliveryAddress', 'deliveryDate'),
            'edit_active.tendering': blacklist('deliveryLocation', 'deliveryAddress', 'deliveryDate'),
        }
    classification = ModelType(CAVClassification, required=True)
    additionalClassifications = ListType(ModelType(Classification), default=list())
    address = ModelType(Address)
    location = ModelType(Location)
    schema_properties = FlexibleModelType(SchemaStore())

    def validate_schema_properties(self, data, new_schema_properties):
        """ Raise validation error if code in schema_properties mismatch
            with classification id """
        if new_schema_properties and not data['classification']['id'].startswith(new_schema_properties['code']):
            raise ValidationError("classification id mismatch with schema_properties code")


class Identifier(BaseIdentifier):
    scheme = StringType(required=True, choices=ORA_CODES)


class Organization(BaseOrganization):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))


class ProcuringEntity(BaseProcuringEntity):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))


class Document(BaseDocument):
    format = StringType(regex='^[-\w]+/[-\.\w\+]+$')
    url = StringType()
    index = IntType()
    accessDetails = StringType()
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
        'illustration', 'auctionProtocol', 'x_dgfPublicAssetCertificate',
        'x_presentation', 'x_nda', 'x_dgfAssetFamiliarization',
        'x_dgfPlatformLegalDetails',
    ])

    @serializable(serialized_name="url", serialize_when_none=False)
    def download_url(self):
        url = self.url
        if not url or '?download=' not in url:
            return url
        doc_id = parse_qs(urlparse(url).query)['download'][-1]
        root = self.__parent__
        parents = []
        while root.__parent__ is not None:
            parents[0:0] = [root]
            root = root.__parent__
        request = root.request
        if not request.registry.docservice_url:
            return url
        if 'status' in parents[0] and parents[0].status in type(parents[0])._options.roles:
            role = parents[0].status
            for index, obj in enumerate(parents):
                if obj.id != url.split('/')[(index - len(parents)) * 2 - 1]:
                    break
                field = url.split('/')[(index - len(parents)) * 2]
                if "_" in field:
                    field = field[0] + field.title().replace("_", "")[1:]
                roles = type(obj)._options.roles
                if roles[role if role in roles else 'default'](field, []):
                    return url
        from openprocurement.api.utils import generate_docservice_url
        if not self.hash:
            path = [i for i in urlparse(url).path.split('/') if len(i) == 32 and not set(i).difference(hexdigits)]
            return generate_docservice_url(request, doc_id, False, '{}/{}'.format(path[0], path[-1]))
        return generate_docservice_url(request, doc_id, False)

    def validate_hash(self, data, hash_):
        doc_type = data.get('documentType')
        if doc_type in (DOCUMENT_TYPE_URL_ONLY + DOCUMENT_TYPE_OFFLINE) and hash_:
            raise ValidationError(u'This field is not required.')

    def validate_format(self, data, format_):
        doc_type = data.get('documentType')
        if doc_type not in (DOCUMENT_TYPE_URL_ONLY + DOCUMENT_TYPE_OFFLINE) and not format_:
            raise ValidationError(u'This field is required.')
        if doc_type in DOCUMENT_TYPE_URL_ONLY and format_:
            raise ValidationError(u'This field is not required.')

    def validate_url(self, data, url):
        doc_type = data.get('documentType')
        if doc_type in DOCUMENT_TYPE_URL_ONLY:
            URLType().validate(url)
        if doc_type in DOCUMENT_TYPE_OFFLINE and url:
            raise ValidationError(u'This field is not required.')
        if doc_type not in DOCUMENT_TYPE_OFFLINE and not url:
            raise ValidationError(u'This field is required.')

    def validate_accessDetails(self, data, accessDetails):
        if data.get('documentType') in DOCUMENT_TYPE_OFFLINE and not accessDetails:
            raise ValidationError(u'This field is required.')


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


class Complaint(BaseComplaint):
    author = ModelType(Organization, required=True)
    documents = ListType(ModelType(Document), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])


class Cancellation(BaseCancellation):
    documents = ListType(ModelType(Document), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])


class Contract(BaseContract):
    items = ListType(ModelType(Item))
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    complaints = ListType(ModelType(Complaint), default=list())
    documents = ListType(ModelType(Document), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])


class Award(BaseAward):
    class Options:
        roles = {
            'create': blacklist('id', 'status', 'date', 'documents', 'complaints', 'complaintPeriod', 'verificationPeriod', 'paymentPeriod', 'signingPeriod'),
            'Administrator': whitelist('verificationPeriod', 'paymentPeriod', 'signingPeriod'),
        }

    def __local_roles__(self):
        auction = get_auction(self)
        for bid in auction.bids:
            if bid.id == self.bid_id:
                bid_owner = bid.owner
                bid_owner_token = bid.owner_token
        return dict([('{}_{}'.format(bid_owner, bid_owner_token), 'bid_owner')])

    def __acl__(self):
        auction = get_auction(self)
        for bid in auction.bids:
            if bid.id == self.bid_id:
                bid_owner = bid.owner
                bid_owner_token = bid.owner_token
        return [(Allow, '{}_{}'.format(bid_owner, bid_owner_token), 'edit_auction_award')]

    # pending status is deprecated. Only for backward compatibility with awarding 1.0
    status = StringType(required=True, choices=['pending.waiting', 'pending.verification', 'pending.payment', 'unsuccessful', 'active', 'cancelled', 'pending'], default='pending.verification')
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    complaints = ListType(ModelType(Complaint), default=list())
    documents = ListType(ModelType(Document), default=list(), validators=[validate_disallow_dgfPlatformLegalDetails])
    items = ListType(ModelType(Item))
    verificationPeriod = ModelType(Period)
    paymentPeriod = ModelType(Period)
    signingPeriod = ModelType(Period)

    @serializable(serialized_name="verificationPeriod", serialize_when_none=False)
    def award_verificationPeriod(self):
        period = self.verificationPeriod
        if not period:
            return
        if not period.endDate:
            auction = get_auction(self)
            period.endDate = calculate_business_date(period.startDate, VERIFY_AUCTION_PROTOCOL_TIME, auction, True)
            round_to_18_hour_delta = period.endDate.replace(hour=18, minute=0, second=0) - period.endDate
            period.endDate = calculate_business_date(period.endDate, round_to_18_hour_delta, auction, False)

        return period.to_primitive()

    @serializable(serialized_name="paymentPeriod", serialize_when_none=False)
    def award_paymentPeriod(self):
        period = self.paymentPeriod
        if not period:
            return
        if not period.endDate:
            auction = get_auction(self)
            period.endDate = calculate_business_date(period.startDate, AWARD_PAYMENT_TIME, auction, True)
            round_to_18_hour_delta = period.endDate.replace(hour=18, minute=0, second=0) - period.endDate
            period.endDate = calculate_business_date(period.endDate, round_to_18_hour_delta, auction, False)
        return period.to_primitive()

    @serializable(serialized_name="signingPeriod", serialize_when_none=False)
    def award_signingPeriod(self):
        period = self.signingPeriod
        if not period:
            return
        if not period.endDate:
            auction = get_auction(self)
            period.endDate = calculate_business_date(period.startDate, CONTRACT_SIGNING_TIME, auction, True)
            round_to_18_hour_delta = period.endDate.replace(hour=18, minute=0, second=0) - period.endDate
            period.endDate = calculate_business_date(period.endDate, round_to_18_hour_delta, auction, False)
        return period.to_primitive()


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
edit_role = (edit_role + blacklist('enquiryPeriod', 'tenderPeriod', 'value', 'auction_value', 'minimalStep', 'auction_minimalStep', 'guarantee', 'auction_guarantee', 'eligibilityCriteria', 'eligibilityCriteria_en', 'eligibilityCriteria_ru', 'awardCriteriaDetails', 'awardCriteriaDetails_en', 'awardCriteriaDetails_ru', 'procurementMethodRationale', 'procurementMethodRationale_en', 'procurementMethodRationale_ru', 'submissionMethodDetails', 'submissionMethodDetails_en', 'submissionMethodDetails_ru', 'items', 'procuringEntity', 'suspended', 'merchandisingObject'))
Administrator_role = (whitelist('suspended', 'awards') + Administrator_role)


@implementer(IAuction)
class Auction(BaseAuction):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    class Options:
        roles = {
            'create': create_role,
            'edit_active.tendering': edit_role,
            'Administrator': Administrator_role,
            'pending.verification': enquiries_role,
            'invalid': view_role,
            'edit_pending.verification': whitelist(),
            'edit_invalid': whitelist(),
            'convoy': whitelist('status', 'items', 'documents')
        }

    awards = ListType(ModelType(Award), default=list())
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the auction.
    cancellations = ListType(ModelType(Cancellation), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
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
    procurementMethodType = StringType(default="dgfOtherAssets")
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(choices=['draft', 'pending.verification', 'invalid', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')
    questions = ListType(ModelType(Question), default=list())
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
        elif not self.lots and self.status == 'active.qualification':
            for award in self.awards:
                if award.status == 'pending.verification':
                    checks.append(award.verificationPeriod.endDate.astimezone(TZ))
                elif award.status == 'pending.payment':
                    checks.append(award.paymentPeriod.endDate.astimezone(TZ))
        elif not self.lots and self.status == 'active.awarded' and not any([
                i.status in self.block_complaint_status
                for i in self.complaints
            ]) and not any([
                i.status in self.block_complaint_status
                for a in self.awards
                for i in a.complaints
            ]):
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in self.awards
                if a.complaintPeriod.endDate
            ]
            for award in self.awards:
                if award.status == 'active':
                    checks.append(award.signingPeriod.endDate.astimezone(TZ))

            last_award_status = self.awards[-1].status if self.awards else ''
            if standStillEnds and last_award_status == 'unsuccessful':
                checks.append(max(standStillEnds))
        elif self.lots and self.status in ['active.qualification', 'active.awarded'] and not any([
                i.status in self.block_complaint_status and i.relatedLot is None
                for i in self.complaints
            ]):
            for lot in self.lots:
                if lot['status'] != 'active':
                    continue
                lot_awards = [i for i in self.awards if i.lotID == lot.id]
                pending_complaints = any([
                    i['status'] in self.block_complaint_status and i.relatedLot == lot.id
                    for i in self.complaints
                ])
                pending_awards_complaints = any([
                    i.status in self.block_complaint_status
                    for a in lot_awards
                    for i in a.complaints
                ])
                standStillEnds = [
                    a.complaintPeriod.endDate.astimezone(TZ)
                    for a in lot_awards
                    if a.complaintPeriod.endDate
                ]
                last_award_status = lot_awards[-1].status if lot_awards else ''
                if not pending_complaints and not pending_awards_complaints and standStillEnds and last_award_status == 'unsuccessful':
                    checks.append(max(standStillEnds))
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
        'x_presentation', 'x_nda',
        'x_dgfPlatformLegalDetails', 'x_dgfAssetFamiliarization',
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
    eligibilityCriteria = StringType(default=u"До участі допускаються лише ліцензовані фінансові установи.")
    eligibilityCriteria_en = StringType(default=u"Only licensed financial institutions are eligible to participate.")
    eligibilityCriteria_ru = StringType(default=u"К участию допускаются только лицензированные финансовые учреждения.")


DGFFinancialAssets = Auction
