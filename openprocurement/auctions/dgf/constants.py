# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openprocurement.api.models import TZ, ORA_CODES


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
DOCUMENT_TYPE_OFFLINE = ['x_dgfAssetFamiliarization']
DOCUMENT_TYPE_URL_ONLY = ['virtualDataRoom', 'x_dgfPublicAssetCertificate', 'x_dgfPlatformLegalDetails']
DGF_PLATFORM_LEGAL_DETAILS = {
    'url': 'http://torgi.fg.gov.ua/prozorrosale',
    'title': u'Місце та форма прийому заяв на участь в аукціоні та банківські реквізити для зарахування гарантійних внесків',
    'documentType': 'x_dgfPlatformLegalDetails',
}
DGF_PLATFORM_LEGAL_DETAILS_FROM = datetime(2016, 12, 23, tzinfo=TZ)

DGF_ID_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)
DGF_DECISION_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)


VERIFY_AUCTION_PROTOCOL_TIME = timedelta(days=4)
AWARD_PAYMENT_TIME = timedelta(days=20)
CONTRACT_SIGNING_TIME = timedelta(days=20)

ELIGIBILITY_CRITERIA = {
    "ua": u"""Учасником електронного аукціону, предметом продажу на яких є права вимоги за кредитними договорами та договорами забезпечення, не може бути користувач, який є позичальником (боржником відносно банку) та/або поручителем (майновим поручителем) за такими кредитними договорами та/або договорами забезпечення.""",
    "ru": u"Участником электронного аукциона, предметом продажи на которых являются права требования по кредитным договорам и договорам обеспечения, не может быть пользователь, являющийся заёмщиком (должником относительно банка) и\или поручителем (имущественным поручителем) по таким кредитным договорам и/или договорам обеспечения.",
    "en": u"The user, who is the borrower (the debtor of the bank) and/or guarantor (property guarantor) for loan agreements and/or collateral agreements, cannot be the bidder of the electronic auction, where the items for sale are the claim rights on such loan agreements and collateral agreements."
}
