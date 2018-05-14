# -*- coding: utf-8 -*-
from openprocurement.auctions.core.adapters import (
    AuctionConfigurator,
    AuctionManagerAdapter
)
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


class AuctionDGFOtherAssetsManagerAdapter(AuctionManagerAdapter):

    def create_auction(self, request):
        pass

    def change_auction(self, request):
        pass


class AuctionDGFFinancialAssetsManagerAdapter(AuctionManagerAdapter):

    def create_auction(self, request):
        pass

    def change_auction(self, request):
        pass
