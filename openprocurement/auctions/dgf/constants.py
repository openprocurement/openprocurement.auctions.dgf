# -*- coding: utf-8 -*-
from datetime import datetime
from openprocurement.api.models import TZ


FINANCIAL_VIEW_LOCATIONS = [
    "openprocurement.auctions.dgf.views.financial",
    "openprocurement.auctions.core.plugins",
]

OTHER_VIEW_LOCATIONS = [
    "openprocurement.auctions.dgf.views.other",
    "openprocurement.auctions.core.plugins",
]

DGF_PLATFORM_LEGAL_DETAILS = {
    'url': 'http://torgi.fg.gov.ua/prozorrosale',
    'title': u'Місце та форма прийому заяв на участь в аукціоні та банківські реквізити для зарахування гарантійних внесків',
    'documentType': 'x_dgfPlatformLegalDetails',
}
DGF_PLATFORM_LEGAL_DETAILS_FROM = datetime(2016, 12, 23, tzinfo=TZ)

DGF_ID_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)
DGF_DECISION_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)

ELIGIBILITY_CRITERIA = {
    "ua": u"""Учасником електронного аукціону, предметом продажу на яких є права вимоги за кредитними договорами та договорами забезпечення, не може бути користувач, який є позичальником (боржником відносно банку) та/або поручителем (майновим поручителем) за такими кредитними договорами та/або договорами забезпечення.""",
    "ru": u"Участником электронного аукциона, предметом продажи на которых являются права требования по кредитным договорам и договорам обеспечения, не может быть пользователь, являющийся заёмщиком (должником относительно банка) и\или поручителем (имущественным поручителем) по таким кредитным договорам и/или договорам обеспечения.",
    "en": u"The user, who is the borrower (the debtor of the bank) and/or guarantor (property guarantor) for loan agreements and/or collateral agreements, cannot be the bidder of the electronic auction, where the items for sale are the claim rights on such loan agreements and collateral agreements."
}

