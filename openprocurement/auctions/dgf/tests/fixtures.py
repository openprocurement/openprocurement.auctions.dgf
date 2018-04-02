from openprocurement.api.models.auction_models.models import get_now
from datetime import timedelta
from openprocurement.auctions.core.plugins.contracting.v3.models import (
    Prolongation,
)


PROLONGATION = {
    'decisionID': 'very_importante_documente',
    'description': 'Prolongate your contract for free!',
    'reason': 'other',
    'documents': [],
    'datePublished': get_now().isoformat(),
}

def create_award(test_case):
    # Create award
    authorization = test_case.app.authorization
    test_case.app.authorization = ('Basic', ('auction', ''))
    now = get_now()
    auction_result = {
        'bids': [
            {
                "id": b['id'],
                "date": (now - timedelta(seconds=i)).isoformat(),
                "value": b['value']
            }
            for i, b in enumerate(test_case.initial_bids)
        ]
    }

    response = test_case.app.post_json(
        '/auctions/{}/auction'.format(test_case.auction_id),
        {'data': auction_result}
    )
    test_case.assertEqual(response.status, '200 OK')
    auction = response.json['data']
    test_case.app.authorization = authorization
    test_case.award = auction['awards'][0]
    test_case.award_id = test_case.award['id']
    test_case.award_value = test_case.award['value']
    test_case.award_suppliers = test_case.award['suppliers']

    test_case.set_status('active.qualification')

    test_case.app.authorization = ('Basic', ('token', ''))
    response = test_case.app.post(
        '/auctions/{}/awards/{}/documents?acc_token={}'.format(
            test_case.auction_id,
            test_case.award_id,
            test_case.auction_token
        ),
        upload_files=[('file', 'auction_protocol.pdf', 'content')]
    )
    test_case.assertEqual(response.status, '201 Created')
    test_case.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']

    response = test_case.app.patch_json(
        '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(
            test_case.auction_id,
            test_case.award_id,
            doc_id,
            test_case.auction_token
        ),
        {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }}
    )
    test_case.assertEqual(response.status, '200 OK')
    test_case.assertEqual(response.content_type, 'application/json')
    test_case.assertEqual(
        response.json["data"]["documentType"],
        'auctionProtocol'
    )
    test_case.assertEqual(response.json["data"]["author"], 'auction_owner')

    test_case.app.patch_json(
        '/auctions/{}/awards/{}'.format(
            test_case.auction_id,
            test_case.award_id
        ),
        {"data": {"status": "pending"}}
    )
    test_case.app.patch_json(
        '/auctions/{}/awards/{}'.format(
            test_case.auction_id,
            test_case.award_id
        ),
        {"data": {"status": "active"}}
    )
    get_auction_response = test_case.app.get(
        '/auctions/{}'.format(
            test_case.auction_id,
        )
    )
    test_case.award_contract_id = get_auction_response.\
        json['data']['contracts'][0]['id']

def create_prolongation(test_case, test_case_attr):
    """Create prolongation and place it's id into test_case arrtibute
    """
    prolongation_post_response = test_case.app.post_json(
        '/auctions/{0}/contracts/{1}/prolongations?acc_token={2}'.format(
            test_case.auction_id,
            test_case.contract_id,
            test_case.auction_token,
        ),
        {'data': PROLONGATION}
    )
    test_case.assertEqual(prolongation_post_response.status, '201 Created')

    prolongation_data = prolongation_post_response.json.get('data', {})
    created_prolongation = Prolongation(prolongation_data)
    created_prolongation.validate() # check returned data
    test_case.assertEqual(
        created_prolongation.decisionID,
        PROLONGATION['decisionID'],
        'Prolongation creation is wrong.'
    )
    setattr(test_case, test_case_attr, created_prolongation.id)

