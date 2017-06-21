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
            edge[label="*" style=solid];
            "pending.verification" -> unsuccessful;
            edge[label="***" style=dashed];
            "pending.payment" -> active;
            edge[label="*****" style=filled];
            "pending.waiting" -> "pending.verification"[label="2nd award only" fontcolor=blue];
            label = "Awarding Process";
            color=blue
        }
            edge[style=dashed];
            "pending.payment" -> "unsuccessful";
            edge[label="****" style=solid];
            "pending.payment" -> unsuccessful;
            edge[label=" **" style=dashed];
            "pending.verification" -> "pending.payment";
            edge[label="*****" style=solid];
            active -> unsuccessful;
            
    }


Legend
--------

 Blue nodes represent statuses for the 2nd award ONLY

 \* no protocol
 
 \*\* protocol required

 \*\*\* payment approved by the organizer

 \*\*\*\* no payment approval

 \*\*\*\*\* contract activation = false by the end of "signingPeriod"


Roles
-----

:Chronograph: solid

:Organizer:  dashed

:Participant: dotted


Procedure Description
---------------------

1. The award with the highest qualifying bid initially receives a "pending.verification" status. The procedure enters the "verificationPeriod" stage, which lasts 0-4 days. Unless the protocol is uploaded and confirmed by the organizer in 4 days, the award receives an "unsuccessful" status. Otherwise, the organizer manually switches the award status to "pending.payment".
2. It is then when the qualification procedure enters the "paymentPeriod" stage, which lasts up to 20 days from the beginning of the highest bidder qualification process. When the organizer confirms that the payment has been received, the award enters the "active" status, while the procedure moves to the status "signingPeriod". This period is the same in length as the "paymentPeriod" - a maximum of 20 days from the start of qualification. If the organizer does not confirm payment by the end of the "paymentPeriod", the award automatically becomes "unsuccessful". The same is true for the signingPeriod - the organizer should upload and activate the contract in the system by the end of the "signingPeriod" in order to successfully finish the qualification procedure. Otherwise - the award will become "unsuccessful" and the qualification of the second highest qualifying bidder will begin given that he/she has not disqualified himself/herself by this time.
3. The second highest qualifying bidder, immediately after the auction ending receives the "pending.waiting" status, in which by default he/she agrees to wait for the end of the qualification of the highest qualifying bidder to be eligible to go through the qualification process if the highest bidder is disqualified. The only action that he/she can make is to manually cancel the award decision - withdraw his security deposit and lose the chance to become a winner of the auction. If he/she does that and the first highest qualifying bidder becomes "unsuccessful" at any point in the awarding process, the procedure receives the "unsuccessful" status. Provided that first award gets disqualified while the second has not disqualified himself/herself, the second award automatically changes its status from "pending.waiting" to "pending.verification", after which he/she undergoes the same qualification procedure as outlined above for the first award.

Notes
-----
1. For the bidder to be qualified and not invalidated, his/her bid should be in the amount of more or equal to the starting price of the auction + the minimal step of the auction.
    
    1.1. In case the first two highest bids do not exceed the amount of starting price + the minimal step, the awards are not being formed at all, and the procedure automatically becomes "unsuccessful"

    1.2 In case the second highest bid is smaller than the starting price + the minimal step, two awards are formed with the smaller one becoming unsuccessful immediately. The first highest bid (if larger than the starting price + minimum step) undergoes the awarding procedure and can win the auction.
2. The organizer can disqualify the award at any stage of the awarding process up until the moment, when the contract has been uploaded and activated in the system.
3. The second highest qualifying bidder can disqualify himself/herself at any point in time BEFORE the start of his/her qualification process.


Statuses
--------

:pending.waiting:
    The second highest valid bidder awaits for the qualification of the first highest valid bidder. The former can choose to refuse to wait and withdraw his security deposit.

:cancelled:
    Terminal status. The second highest valid bidder chose to withdraw his security deposit and not to wait for the highest valid bidder to be disqualified.

:pending.verification:
    Awaiting protocol upload and confirmation by the liquidator. The highest valid bidder is able to submit the protocol as well, although it is not sufficient to move to the next status. 

:pending.payment:
    Awaiting payment. Organizer can change the status to active by confirming the payment has been received. 

:active:
    Awaiting for the contract to be signed (uploaded and activated in the system by the organizer). After the end of the "signingPeriod", the status becomes terminal.

:unsuccessful:
    Terminal status. The auction was unsuccessful. Can be switched to either automatically, from any of the previous statuses or by the organizer.
