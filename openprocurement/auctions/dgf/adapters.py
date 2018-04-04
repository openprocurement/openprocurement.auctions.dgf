# -*- coding: utf-8 -*-
from openprocurement.auctions.core.adapters import AuctionConfigurator
from openprocurement.auctions.dgf.models import (
    DGFOtherAssets,
    DGFFinancialAssets
)
from openprocurement.auctions.core.plugins.awarding.v3.adapters import (
    AwardingV3ConfiguratorMixin
)


class AuctionDGFOtherAssetsConfigurator(AuctionConfigurator,
                                        AwardingV3ConfiguratorMixin):
    name = 'Auction Dgf Configurator'
    model = DGFOtherAssets


class AuctionDGFFinancialAssetsConfigurator(AuctionConfigurator,
                                            AwardingV3ConfiguratorMixin):
    name = 'Auction Dgf Configurator'
    model = DGFFinancialAssets
