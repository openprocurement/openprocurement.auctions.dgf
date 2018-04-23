import logging

from pyramid.interfaces import IRequest
from openprocurement.auctions.dgf.models import (
    IDgfAuction,
    DGFOtherAssets,
    DGFFinancialAssets
)
from openprocurement.auctions.dgf.adapters import (
    AuctionDGFOtherAssetsConfigurator,
    AuctionDGFFinancialAssetsConfigurator
)
from openprocurement.auctions.core.plugins.awarding.v3.adapters import (
    AwardingNextCheckV3
)
from openprocurement.auctions.core.includeme import (
    IContentConfigurator,
    IAwardingNextCheck
)
from openprocurement.auctions.dgf.constants import (
    FINANCIAL_VIEW_LOCATIONS,
    OTHER_VIEW_LOCATIONS,
    DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER,
    DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL
)

LOGGER = logging.getLogger(__name__)


def includeme_other(config, plugin_config=None):
    procurement_method_types = plugin_config.get('aliases', [])
    if plugin_config.get('use_default', False):
        procurement_method_types.append(DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER)
    for procurementMethodType in procurement_method_types:
        config.add_auction_procurementMethodType(DGFOtherAssets,
                                                 procurementMethodType)

    for view_location in OTHER_VIEW_LOCATIONS:
        config.scan(view_location)

    # Register adapters
    config.registry.registerAdapter(
        AuctionDGFOtherAssetsConfigurator,
        (IDgfAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AwardingNextCheckV3,
        (IDgfAuction, ),
        IAwardingNextCheck
    )

    LOGGER.info("Included openprocurement.auctions.dgf.financial plugin",
                extra={'MESSAGE_ID': 'included_plugin'})


def includeme_financial(config, plugin_config=None):
    procurement_method_types = plugin_config.get('aliases', [])
    if plugin_config.get('use_default', False):
        procurement_method_types.append(
            DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL
        )
    for procurementMethodType in procurement_method_types:
        config.add_auction_procurementMethodType(DGFFinancialAssets,
                                                 procurementMethodType)

    for view_location in FINANCIAL_VIEW_LOCATIONS:
        config.scan(view_location)

    # Register Adapters
    config.registry.registerAdapter(
        AuctionDGFFinancialAssetsConfigurator,
        (IDgfAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AwardingNextCheckV3,
        (IDgfAuction, ),
        IAwardingNextCheck
    )

    LOGGER.info("Included openprocurement.auctions.dgf.other plugin",
                extra={'MESSAGE_ID': 'included_plugin'})
