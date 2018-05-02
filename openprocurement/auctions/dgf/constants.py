# -*- coding: utf-8 -*-
from datetime import datetime
from openprocurement.auctions.core.utils import TZ


FINANCIAL_VIEW_LOCATIONS = [
    "openprocurement.auctions.dgf.views.financial",
    "openprocurement.auctions.core.plugins",
]

OTHER_VIEW_LOCATIONS = [
    "openprocurement.auctions.dgf.views.other",
    "openprocurement.auctions.core.plugins",
]

DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER = "exampleDGFOther"
DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL = "exampleDGFFinancial"
