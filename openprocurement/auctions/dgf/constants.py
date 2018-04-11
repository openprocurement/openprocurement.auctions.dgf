# -*- coding: utf-8 -*-
from datetime import datetime
from openprocurement.api.models import TZ


FINANCIAL_VIEW_LOCATIONS = [
    "openprocurement.auctions.dgf.views.financial",
]

OTHER_VIEW_LOCATIONS = [
    "openprocurement.auctions.dgf.views.other",
]

DGF_ID_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)
DGF_DECISION_REQUIRED_FROM = datetime(2017, 1, 1, tzinfo=TZ)
