from openprocurement.auctions.dgf.models import DGFOtherAssets, DGFFinancialAssets


def includeme(config):
    config.add_auction_procurementMethodType(DGFOtherAssets)
    config.scan("openprocurement.auctions.dgf.views.other")

    config.add_auction_procurementMethodType(DGFFinancialAssets)
    config.scan("openprocurement.auctions.dgf.views.financial")
