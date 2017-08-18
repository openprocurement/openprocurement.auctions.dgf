# -*- coding: utf-8 -*-
from openprocurement.auctions.core.validation import validate_json_data, validate_data


def validate_patch_auction_data(request):
    data = validate_json_data(request)
    if data is None:
        return
    if ((request.context.status == 'active.tendering' and
            data.get('status') == 'invalid') or (
                request.context.status == 'invalid' and
                data.get('status') == 'active.tendering')):
        request.errors.add(
            'body', 'data',
            'Can\'t update auction in current ({}) status'.format(
                request.context.status))
        request.errors.status = 403
        return
    if request.context.status not in ['draft', 'pending.verification']:
        return validate_data(request, type(request.auction), True, data)
    default_statuses = [type(request.auction).fields['status'].default,
                        'pending.verification', 'invalid']
    if data.get('status') not in default_statuses :
        request.errors.add(
            'body', 'data', 'Can\'t update auction in current (draft) status')
        request.errors.status = 403
        return
    if (data.get('status') == 'pending.verification' and
            not getattr(request.context, 'lotID')):
        request.errors.add(
            'body', 'data',
            'Can\'t switch auction to status (pending.verification) without'
            ' lotID')
        request.errors.status = 422
        return
    request.validated['data'] = {'status': data['status']}
    request.context.status = data['status']