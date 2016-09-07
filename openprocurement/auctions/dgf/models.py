# -*- coding: utf-8 -*-
from schematics.types import StringType
from schematics.types.compound import ModelType
from zope.interface import implementer
from openprocurement.api.models import ListType
from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.flash.models import (
    Auction as BaseAuction, Document as BaseDocument, Bid as BaseBid,
    Complaint as BaseComplaint, Cancellation as BaseCancellation,
    Contract as BaseContract, Award as BaseAward,
)


class Document(BaseDocument):

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
    ])


class Bid(BaseBid):

    documents = ListType(ModelType(Document), default=list())


class Complaint(BaseComplaint):

    documents = ListType(ModelType(Document), default=list())


class Cancellation(BaseCancellation):

    documents = ListType(ModelType(Document), default=list())


class Contract(BaseContract):

    documents = ListType(ModelType(Document), default=list())


class Award(BaseAward):
    complaints = ListType(ModelType(Complaint), default=list())
    documents = ListType(ModelType(Document), default=list())


@implementer(IAuction)
class Auction(BaseAuction):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    contracts = ListType(ModelType(Contract), default=list())
    cancellations = ListType(ModelType(Cancellation), default=list())
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the auction.
    awards = ListType(ModelType(Award), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the auction.
    procurementMethodType = StringType(default="dgfOtherAssets")
