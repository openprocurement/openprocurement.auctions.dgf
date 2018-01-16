# -*- coding: utf-8 -*-
from openprocurement.auctions.core.adapters import AuctionConfigurator
from openprocurement.auctions.dgf.models import DGFOtherAssets, DGFFinancialAssets
from openprocurement.auctions.core.plugins.awarding.v3.utils import create_awards_dgf
from openprocurement.auctions.core.plugins.awarding.v3.models import Award


class AuctionDGFOtherAssetsConfigurator(AuctionConfigurator):
    name = 'Auction Dgf Configurator'
    model = DGFOtherAssets
    award_model = Award

    def add_award(self):
        return create_awards_dgf(self.request)


class AuctionDGFFinancialAssetsConfigurator(AuctionConfigurator):
    name = 'Auction Dgf Configurator'
    model = DGFFinancialAssets
    award_model = Award

    def add_award(self):
        return create_awards_dgf(self.request)
