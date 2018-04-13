.. _award_workflow: 

Award Workflow
==============

For a more detailed information see :ref:`award`

    * :ref:`Qualification`
    * :ref:`Confirming_qualification`
    * :ref:`Candidate_disqualification`
    * :ref:`Waiting_refusal`

.. graphviz::

    digraph G {
        subgraph cluster_1 {
            node [style=filled, color=lightblue];
            edge[style=dotted];
            "pending.waiting" -> cancelled[label="2nd award only" fontcolor=blue];
            node [style=filled, color=lightgrey];
            edge[label="***" style=solid];
            "pending" -> unsuccessful;
            edge[label="**" style=dashed];
            "pending" -> "acive";
            edge[label="*" style=solid];
            "pending.waiting" -> "pending";
            label = "Awarding Process";
            color=blue
        }

.. graphviz::

    digraph G {
        subgraph cluster_1 {
            node [style=filled, color=lightgrey];
            edge[label="**" style=solid];
            "pending" -> "cancelled";
            edge[label="*" style=dashed];
            "pending" -> "active"
            label = "Contract Workflow";
            color=blue
    }

Legend
--------

 Blue nodes represent statuses for the 2nd award ONLY

 \* award for winner is always formed in `pending`.
 
 \*\* protocol is downloaded and award is switched to `active` by the organizer.

 \*\*\* auction protocol was not uploaded and award was not activated


Roles
-----

:Chronograph: solid

:Organizer:  dashed

:Participant: dotted


.. graphviz::

    digraph G {
        subgraph cluster_1 {
            node [style=filled, color=lightgrey];
            edge[label="**" style=solid];
            "pending" -> "cancelled";
            edge[label="*" style=dashed];
            "pending" -> "active"
            label = "Contract Workflow";
            color=blue
    }

Legend
--------

 \* document was downloaded to contract. The contract itself was successfully activated by the organizer.

 \*\* there was no document uploaded. The organizer din not activate the contract.


Procedure Description
---------------------

1. The award with the highest qualifying bid initially receives a `pending` status. The procedure enters the `verificationPeriod` stage, which lasts 0-4 business days. Unless the protocol is uploaded and confirmed by the organizer in 4 business days, the award receives an `unsuccessful` status. Otherwise, the organizer manually switches the award status to `active`. Simultaneously, the contract is being created in `pending` status.
2. It is then when the qualification procedure enters the `signingPeriod` stage, which lasts up to 20 business days from the beginning of the highest bidder qualification process. Within this time, the organizer can optionally set the day when the payment has been received. Also the organizer should upload and activate the contract in the system by the end of the `signingPeriod` in order to successfully finish the qualification procedure. Otherwise - the contract will become `cancelled` and the qualification of the second highest qualifying bidder will begin given that they have not disqualified themselves by this time.
3. The second highest qualifying bidder, immediately after the auction ending receives the `pending.waiting` status, in which by default they agree to wait for the end of the qualification of the highest qualifying bidder to be eligible to go through the qualification process if the highest bidder is disqualified. The only action that they can make is to manually cancel the award decision - withdraw the security deposit and lose the chance to become a winner of the auction. If that is done and the first highest qualifying bidder becomes `unsuccessful`, the procedure receives the `unsuccessful` status. Provided that first award gets disqualified while the second has not disqualified themselves, the second award automatically changes its status from `pending.waiting` to `pending`, after which they undergo the same qualification procedure as outlined above for the first award.

Notes
-----
1. For the bidder to be qualified and not invalidated, the bid should be in the amount of more or equal to the starting price of the auction + the minimal step of the auction.

    1.1. In case the first two highest bids do not exceed the amount of starting price + the minimal step, the awards are not being formed at all, and the procedure automatically becomes "unsuccessful"

    1.2 In case the second highest bid is smaller than the starting price + the minimal step, two awards are formed with the smaller one becoming unsuccessful immediately. The first highest bid (if larger than the starting price + minimum step) undergoes the awarding procedure and can win the auction.

2. The organizer can disqualify the award at any stage of the awarding process up to the moment, when the contract is created in the system.
3. The second highest qualifying bidder can disqualify themselves at any point in time BEFORE the start of their qualification process.

Statuses
--------

:pending.waiting:
    The second highest valid bidder awaits for the qualification of the first highest valid bidder. The former can choose to refuse to wait and withdraw his security deposit.

:cancelled:
    Terminal status.

:pending:
    :`Award`: Awaiting protocol upload and confirmation by the organizer. The highest valid bidder is able to submit the protocol as well, although it is not sufficient to move to the next status.

    :`Contract`: Awaiting for the contract to be signed (uploaded and activated in the system by the organizer). After the end of the "signingPeriod", the status becomes terminal.

:active:
    :`Award`: Auction protocol was downloaded so that the award could be switched to `active` by the organizer.

    :`Contract`: The document was downloaded to contract so that the status of the object could be switched to `active` by the organizer.

:unsuccessful:
    Terminal status.

