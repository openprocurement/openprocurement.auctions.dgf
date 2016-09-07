# -*- coding: utf-8 -*-
from openprocurement.auctions.dgf.models import Auction


def auction_from_data(request, data, raise_error=True, create=True):
    #procurementMethodType = data.get('procurementMethodType', 'belowThreshold')
    #model = request.registry.auction_procurementMethodTypes.get(procurementMethodType)
    #if model is None and raise_error:
    #    request.errors.add('data', 'procurementMethodType', 'Not implemented')
    #    request.errors.status = 415
    #    raise error_handler(request.errors)
    #update_logging_context(request, {'auction_type': procurementMethodType})
    #if model is not None and create:
    #    model = model(data)
    #return model
    if create:
        return Auction(data)
    return Auction
