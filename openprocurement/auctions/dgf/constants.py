# -*- coding: utf-8 -*-
from datetime import timedelta


FINANCIAL_VIEW_LOCATIONS = [
    "openprocurement.auctions.dgf.views.financial",
]

OTHER_VIEW_LOCATIONS = [
    "openprocurement.auctions.dgf.views.other",
]

DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER = "DGFOtherAssets"
DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL = "DGFFinancialAssets"
DEFAULT_LEVEL_OF_ACCREDITATION = {'create': [1],
                                  'edit': [2]}

RECTIFICATION_PERIOD_DURATION = timedelta(days=2)
