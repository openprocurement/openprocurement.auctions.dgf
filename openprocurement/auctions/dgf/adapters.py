# -*- coding: utf-8 -*-
from openprocurement.auctions.core.adapters import AuctionConfigurator
from openprocurement.auctions.dgf.models import DGFOtherAssets, DGFFinancialAssets


class AuctionDGFOtherAssetsConfigurator(AuctionConfigurator):
    name = 'Auction Dgf Configurator'
    model = DGFOtherAssets


class AuctionDGFFinancialAssetsConfigurator(AuctionConfigurator):
    name = 'Auction Dgf Configurator'
    model = DGFFinancialAssets