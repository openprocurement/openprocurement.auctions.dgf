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

    if request.context.status == 'draft':
        if data.get('status') not in [default_status, 'pending.verification']:
            request.errors.add(
                'body', 'data', 'Can\'t update auction in current (draft) status')
            request.errors.status = 403
            return
        elif data.get('status') == 'pending.verification' and not getattr(request.context, 'lotID'):
            request.errors.add(
                'body', 'data', 'Can\'t switch auction to status (pending.verification) without lotID')
            request.errors.status = 422
            return
    elif request.context.status == 'pending.verification':
        if data.get('status') not in [default_status, 'invalid'] or request.authenticated_role != 'convoy':
            request.errors.add(
                'body', 'data', 'Can\'t update auction in current (pending.verification) status')
            request.errors.status = 403
            return
        elif data.get('status') == 'invalid':
            return validate_data(request, type(request.auction), True, data)
        elif data.get('status') == default_status:
            request.validated['data'] = {'status': data['status']}
            request.context.status = data['status']
            return validate_data(request, type(request.auction), True, data)

    request.validated['data'] = {'status': data['status']}
    request.context.status = data['status']