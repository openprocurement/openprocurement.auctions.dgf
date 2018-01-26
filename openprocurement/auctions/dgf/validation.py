# -*- coding: utf-8 -*-
from openprocurement.auctions.core.validation import validate_json_data, validate_data


def validate_patch_auction_data(request):
    data = validate_json_data(request)
    if data is None:
        return
    if request.authenticated_role == 'convoy' and request.context.status != "pending.verification":
        request.errors.add('body', 'data', 'Can\'t update auction in current ({}) status'.format(request.context.status))
        request.errors.status = 403
        return
    if request.context.status not in ['draft', 'pending.verification']:
        return validate_data(request, type(request.auction), True, data)
    default_status = type(request.auction).fields['status'].default
    new_status = data.get('status', '')

    if request.context.status == 'draft':
        if not new_status or new_status not in [default_status, 'pending.verification']:
            request.errors.add('body', 'data',
                               'Can\'t update auction in current ({}) status'.format(request.context.status))
            request.errors.status = 403
            return
        elif new_status == 'pending.verification':
            if not getattr(request.context, 'merchandisingObject'):
                request.errors.add(
                    'body', 'data', 'Can\'t switch auction to status (pending.verification) without merchandisingObject')
                request.errors.status = 422
                return
            elif request.context.items:
                request.errors.add('body', 'items', 'This field is not required.')
                request.errors.status = 422
                return
            elif request.context.dgfID:
                request.errors.add('body', 'dgfID', 'This field is not required.')
                request.errors.status = 422
                return

        request.validated['data'] = {'status': new_status}
        request.context.status = new_status
        return

    elif request.context.status == 'pending.verification':
        if request.authenticated_role != 'convoy' or \
                (new_status and new_status not in ['invalid', 'pending.verification', default_status]):
            request.errors.add('body', 'data',
                               'Can\'t update auction in current ({}) status'.format(request.context.status))
            request.errors.status = 403
            return
        elif new_status == default_status:
            request.validated['data'] = {'status': new_status}
            request.context.status = new_status

        return validate_data(request, type(request.auction), True, data)
