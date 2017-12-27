from pyramid.interfaces import IRequest
from openprocurement.auctions.dgf.models import DGFOtherAssets, DGFFinancialAssets
from openprocurement.auctions.dgf.adapters import (
    AuctionDGFOtherAssetsConfigurator,
    AuctionDGFFinancialAssetsConfigurator
)
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.auctions.core.models import IAuction


def includeme_other(config):
    config.add_auction_procurementMethodType(DGFOtherAssets)
    config.scan("openprocurement.auctions.dgf.views.other")
    config.registry.registerAdapter(AuctionDGFOtherAssetsConfigurator, (IAuction, IRequest),
                                    IContentConfigurator)


def includeme_financial(config):
    config.add_auction_procurementMethodType(DGFFinancialAssets)
    config.scan("openprocurement.auctions.dgf.views.financial")
    config.registry.registerAdapter(AuctionDGFFinancialAssetsConfigurator, (IAuction, IRequest),
                                    IContentConfigurator)