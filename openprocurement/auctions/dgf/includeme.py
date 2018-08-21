import logging

from pyramid.interfaces import IRequest
from openprocurement.auctions.dgf.models import (
    IDgfOtherAssetsAuction,
    IDgfFinancialAssetsAuction,
    DGFOtherAssets,
    DGFFinancialAssets
)
from openprocurement.auctions.dgf.adapters import (
    AuctionDGFOtherAssetsConfigurator,
    AuctionDGFFinancialAssetsConfigurator,
    AuctionDGFOtherAssetsManagerAdapter,
    AuctionDGFFinancialAssetsManagerAdapter
)
from openprocurement.auctions.core.plugins.awarding.v3.adapters import (
    AwardingNextCheckV3
)
from openprocurement.auctions.core.includeme import (
    IContentConfigurator,
    IAwardingNextCheck
)
from openprocurement.auctions.core.interfaces import (
    IAuctionManager
)
from openprocurement.auctions.dgf.constants import (
    FINANCIAL_VIEW_LOCATIONS,
    OTHER_VIEW_LOCATIONS,
    DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER,
    DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL,
    DEFAULT_LEVEL_OF_ACCREDITATION
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
        (IDgfOtherAssetsAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AwardingNextCheckV3,
        (IDgfOtherAssetsAuction, ),
        IAwardingNextCheck
    )
    config.registry.registerAdapter(
        AuctionDGFOtherAssetsManagerAdapter,
        (IDgfOtherAssetsAuction, ),
        IAuctionManager
    )

    LOGGER.info("Included openprocurement.auctions.dgf.financial plugin",
                extra={'MESSAGE_ID': 'included_plugin'})

    # add accreditation level
    if not plugin_config.get('accreditation'):
        config.registry.accreditation['auction'][DGFOtherAssets._internal_type] = DEFAULT_LEVEL_OF_ACCREDITATION
    else:
        config.registry.accreditation['auction'][DGFOtherAssets._internal_type] = plugin_config['accreditation']

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
        (IDgfFinancialAssetsAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AwardingNextCheckV3,
        (IDgfFinancialAssetsAuction, ),
        IAwardingNextCheck
    )
    config.registry.registerAdapter(
        AuctionDGFFinancialAssetsManagerAdapter,
        (IDgfFinancialAssetsAuction, ),
        IAuctionManager
    )

    LOGGER.info("Included openprocurement.auctions.dgf.other plugin",
                extra={'MESSAGE_ID': 'included_plugin'})
    # add accreditation level
    if not plugin_config.get('accreditation'):
        config.registry.accreditation['auction'][DGFFinancialAssets._internal_type] = DEFAULT_LEVEL_OF_ACCREDITATION
    else:
        config.registry.accreditation['auction'][DGFFinancialAssets._internal_type] = plugin_config['accreditation']
