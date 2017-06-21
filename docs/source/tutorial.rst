.. _tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/auctions` endpoint:

.. include:: tutorial/auction-listing.http
   :code:

Just invoking it reveals empty set.

Now let's attempt creating some auction:

.. include:: tutorial/auction-post-attempt.http
   :code:

Error states that the only accepted Content-Type is `application/json`.

Let's satisfy the Content-type requirement:

.. include:: tutorial/auction-post-attempt-json.http
   :code:

Error states that no `data` has been found in JSON body.


.. index:: Auction

Creating auction
----------------

Let's create auction with the minimal data set (only required properties):

.. include:: tutorial/auction-post-attempt-json-data.http
   :code:

Success! Now we can see that new object has been created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created auction: its internal
`id` (that matches the `Location` segment), its official `auctionID` and
`dateModified` datestamp stating the moment in time when auction has been last
modified. Pay attention to the `procurementMethodType`. Note that auction is
created with `active.tendering` status.

Let's access the URL of the created object (the `Location` header of the response):

.. include:: tutorial/blank-auction-view.http
   :code:

We can see the same response we got after creating auction.

Let's see what listing of auctions reveals us:

.. include:: tutorial/initial-auction-listing.http
   :code:

We do see the auction's internal `id` (that can be used to construct full URL by prepending `https://api-sandbox.ea.openprocurement.org/api/0/auctions/`) and its `dateModified` datestamp.

The previous auction contained only required fields. Let's try creating auction with more data
(auction has status `created`):

.. include:: tutorial/create-auction-procuringEntity.http
   :code:

And again we have `201 Created` response code, `Location` header and body with extra `id`, `auctionID`, and `dateModified` properties.

Let's check what auction registry contains:

.. include:: tutorial/auction-listing-after-procuringEntity.http
   :code:

And indeed we have 2 auctions now.


Modifying auction
-----------------

Let's update auction by supplementing it with all other essential properties:

.. include:: tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing auction data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. include:: tutorial/auction-listing-after-patch.http
   :code:


.. index:: Document

Uploading documentation
-----------------------

Organizer can upload PDF files into the created auction. Uploading should
follow the :ref:`upload` rules.

.. include:: tutorial/upload-auction-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. include:: tutorial/auction-documents.http
   :code:

The single array element describes the uploaded document. We can upload more documents:

.. include:: tutorial/upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. include:: tutorial/auction-documents-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. include:: tutorial/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. include:: tutorial/auction-documents-3.http
   :code:


.. index:: Enquiries, Question, Answer

Uploading illustration
-----------------------

Organizer can upload illustration files into the created auction. Uploading should
follow the :ref:`upload` rules.

In order to specify illustration display order, `index` field can be used (for details see :ref:`document`). Since this illustration should be displayed first, it has ``"index": 1``.

.. include:: tutorial/upload-first-auction-illustration.http
   :code:

We can check whether illustration is uploaded.

.. include:: tutorial/auction-documents-4.http
   :code:

Organizer can upload second illustration. This illustration should be displayed second, so it has ``"index": 2``.

.. include:: tutorial/upload-second-auction-illustration.http
   :code:

Add third illustration:

.. include:: tutorial/upload-third-auction-illustration.http
   :code:

Note that `index` of the third illustration is the same as for the second illustration: ``"index": 2``. In such cases firstly will be displayed illustration that was uploaded earlier.

We can check that there are three uploaded illustrations.

.. include:: tutorial/auction-documents-5.http
   :code:

Enquiries
---------

When auction is in `active.tendering` status, interested parties can ask questions:

.. include:: tutorial/ask-question.http
   :code:

Organizer can answer them:

.. include:: tutorial/answer-question.http
   :code:

And one can retrieve the question list:

.. include:: tutorial/list-question.http
   :code:

Or an individual answer:

.. include:: tutorial/get-answer.http
   :code:


.. index:: Bidding

Registering bid
---------------

Bidder can register a bid in `draft` status:

.. include:: tutorial/register-bidder.http
   :code:

And activate a bid:

.. include:: tutorial/activate-bidder.http
   :code:

And upload proposal document:

.. include:: tutorial/upload-bid-proposal.http
   :code:

It is possible to check the uploaded documents:

.. include:: tutorial/bidder-documents.http
   :code:

For the best effect (biggest economy) auction should have multiple bidders registered:

.. include:: tutorial/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Auction.auctionUrl`:

.. include:: tutorial/auction-url.http
   :code:

And bidders can find out their participation URLs via their bids:

.. include:: tutorial/bidder-participation-url.http
   :code:

See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. include:: tutorial/bidder2-participation-url.http
   :code:

.. _Qualification:

Qualification
-------------
After the competitive auction two `awards` are created:
 * for the first candidate (a participant that has submitted the highest valid bid at the auction) - initially has a `pending.verification` status and awaits auction protocol to be uploaded by the organizer;
 * for the second candidate (a participant that has submitted the second highest valid bid at the auction).

There are two more scenarios that can happen after the competitive auction:
 * If the two highest bidders have invalid bids (lower than auction starting price + minimal step), the awards will not be created at all, and the qualification procedure will automatically receive the "unsuccessful" status. 
 * If the second highest bidder has a bid that is less than the starting price + minimal step, two awards are created, with one of them receiving a pending.verification status and undergoing the qualification procedure, and the other (with an invalid bid) automatically becoming "unsuccessful".


.. include:: tutorial/get-awards.http
  :code:


.. _Confirming_qualification:

Confirming qualification
~~~~~~~~~~~~~~~~~~~~~~~~


The organizer **must** upload and confirm the auction protocol `auctionProtocol` and add it to the award within **4 business days after the start of the qualification procedure**. The candidate still has a possibility to upload the protocol, but it is neither mandatory, nor sufficient to move to the next status. If the auction protocol has not been uploaded before the end of `verificationPeriod`, the `award` is automatically transferred to the `unsuccessful` status.


.. include:: tutorial/bidder-auction-protocol.http
  :code:

.. include:: tutorial/owner-auction-protocol.http
  :code:



It is the organizer's duty to upload and confirm the protocol, although the award will not switch the status to "pending.payment" automatically.


.. include:: tutorial/verify-protocol.http
 :code:


Within **20 business days after becoming a candidate** he/she must provide payment and organizer has the same time to confirm the payment. Otherwise, the award will automatically become "unsuccessful":


.. include:: tutorial/confirm-qualification.http
  :code:

.. _Candidate_disqualification:

Disqualification of a candidate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In case of manual disqualification, the organizer has to upload file with cancellation reason:


.. include:: qualification/award-active-unsuccessful-upload.http
  :code:


And disqualify candidate:


.. include:: qualification/award-active-disqualify.http
  :code:


Within 20 business days since becoming candidate a new candidate must confirm qualification with steps described above (:ref:`Qualification`).

.. _Waiting_refusal:

Refusal of waiting by another participant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The second candidate (participant that has submitted the second highest valid bid at the auction) can refuse to wait for the disqualification of the first candidate:


.. include:: qualification/award-waiting-cancel.http
  :code:

Signing contract
----------------

The candidate has **20 business days after becoming a candidate** to conclude a contract with the bank based on the results of electronic auction.

Uploading contract documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can upload contract documents. Let's upload contract document:

.. include:: tutorial/auction-contract-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm that document has been added.

Let's see the list of contract documents:

.. include:: tutorial/auction-contract-get-documents.http
   :code:

We can add another contract document:

.. include:: tutorial/auction-contract-upload-second-document.http
   :code:

`201 Created` response code and `Location` header confirm that the second document has been uploaded.

Let's see the list of all added contract documents:

.. include:: tutorial/auction-contract-get-documents-again.http
   :code:

Contract registration
~~~~~~~~~~~~~~~~~~~~~

There is a possibility to set custom contract signature date.
If the date is not set it will be generated on contract registration.
You can register contract:

.. include:: tutorial/auction-contract-sign.http
   :code:

Cancelling auction
------------------

Organizer can cancel auction anytime (except when auction has terminal status e.g. `unsuccesfull`, `canceled`, `complete`).

The following steps should be applied:

1. Prepare cancellation request.
2. Fill it with the protocol describing the cancellation reasons.
3. Cancel the auction with the reasons prepared.

Only the request that has been activated (3rd step above) has power to
cancel auction.  I.e.  you have to not only prepare cancellation request but
to activate it as well.

See :ref:`cancellation` data structure for details.

Preparing the cancellation request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You should pass `reason`, `status` defaults to `pending`. `id` is
autogenerated and passed in the `Location` header of response.

.. include:: tutorial/prepare-cancellation.http
   :code:


Filling cancellation with protocol and supplementary documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Upload the file contents:

.. include:: tutorial/upload-cancellation-doc.http
   :code:

Change the document description and other properties:

.. include:: tutorial/patch-cancellation.http
   :code:

Upload new version of the document:

.. include:: tutorial/update-cancellation-doc.http
   :code:

Activating the request and cancelling auction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: tutorial/active-cancellation.http
   :code:
