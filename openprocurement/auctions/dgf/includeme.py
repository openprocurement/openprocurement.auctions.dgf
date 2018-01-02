from pyramid.interfaces import IRequest
from openprocurement.auctions.dgf.models import (
    DGFOtherAssets,
    DGFFinancialAssets
)
from openprocurement.auctions.dgf.adapters import (
    AuctionDGFOtherAssetsConfigurator,
    AuctionDGFFinancialAssetsConfigurator
)
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.dgf.constants import (
    FINANCIAL_VIEW_LOCATIONS,
    OTHER_VIEW_LOCATIONS,
)


def includeme_other(config):
    config.add_auction_procurementMethodType(DGFOtherAssets)

    for view_location in OTHER_VIEW_LOCATIONS:
        config.scan(view_location)

    config.registry.registerAdapter(
        AuctionDGFOtherAssetsConfigurator,
        (IAuction, IRequest),
        IContentConfigurator
    )


def includeme_financial(config):
    config.add_auction_procurementMethodType(DGFFinancialAssets)

    for view_location in FINANCIAL_VIEW_LOCATIONS:
        config.scan(view_location)

    config.registry.registerAdapter(
        AuctionDGFFinancialAssetsConfigurator,
        (IAuction, IRequest),
        IContentConfigurator
    )

