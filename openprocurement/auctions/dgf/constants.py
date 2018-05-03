# -*- coding: utf-8 -*-
from datetime import datetime
from openprocurement.auctions.core.utils import TZ


FINANCIAL_VIEW_LOCATIONS = [
    "openprocurement.auctions.dgf.views.financial",
]

OTHER_VIEW_LOCATIONS = [
    "openprocurement.auctions.dgf.views.other",
]

DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER = "exampleDGFOther"
DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL = "exampleDGFFinancial"
