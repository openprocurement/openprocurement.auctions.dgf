from pyramid.interfaces import IRequest
from openprocurement.auctions.dgf.models import DGFOtherAssets, DGFFinancialAssets
from openprocurement.auctions.dgf.adapters import AuctionDgfConfigurator
from openprocurement.auctions.core.interfaces import IContentConfigurator
from openprocurement.auctions.core.models import IAuction


def includeme(config):
    config.add_auction_procurementMethodType(DGFOtherAssets)
    config.scan("openprocurement.auctions.dgf.views.other")

    config.add_auction_procurementMethodType(DGFFinancialAssets)
    config.scan("openprocurement.auctions.dgf.views.financial")
    config.registry.registerAdapter(AuctionDgfConfigurator, (IAuction, IRequest),
                                    IContentConfigurator)