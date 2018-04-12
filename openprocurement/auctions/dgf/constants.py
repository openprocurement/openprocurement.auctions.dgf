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

DGF_ID_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)
DGF_DECISION_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)
