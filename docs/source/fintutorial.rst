.. _fintutorial:

Fin. Tutorial
=============

Creating auction
----------------

Let's create auction with the minimal data set (only required properties):

.. include:: tutorial/finauction-post-attempt-json-data.http
   :code:

Success! Now we can see that new object has been created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created auction: its internal
`id` (that matches the `Location` segment), its official `auctionID` and
`dateModified` datestamp stating the moment in time when auction has been last
modified. Pay attention to the `procurementMethodType`. Note that auction is
created with `active.tendering` status.

Let's access the URL of the created object (the `Location` header of the response):

.. include:: tutorial/blank-finauction-view.http
   :code:

We can see the same response we got after creating auction.

Let's see what listing of auctions reveals us:

.. include:: tutorial/initial-finauction-listing.http
   :code:

We do see the auction's internal `id` (that can be used to construct full URL by prepending `https://api-sandbox.ea.openprocurement.org/api/0/auctions/`) and its `dateModified` datestamp.

.. index:: Document, VDR

Uploading documentation
-----------------------

Organizer can upload PDF files into the created auction. Uploading should
follow the :ref:`upload` rules.

.. include:: tutorial/upload-finauction-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. include:: tutorial/finauction-documents.http
   :code:

The single array element describes the uploaded document. We can upload more documents:

.. include:: tutorial/finauction-upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. include:: tutorial/finauction-documents-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. include:: tutorial/finauction-update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. include:: tutorial/finauction-documents-3.http
   :code:

Adding virtual data room
------------------------

Organizer can add URL for virtual data room:

.. include:: tutorial/finauction-adding-vdr.http
   :code:


.. index:: Bidding

Registering bid
---------------

Bidder can register a bid in `draft` status:

.. include:: tutorial/register-finbidder.http
   :code:

And activate a bid:

.. include:: tutorial/activate-finbidder.http
   :code:

And upload license (with ``documentType: financialLicense``):

.. include:: tutorial/upload-finbid-proposal.http
   :code:

It is possible to check the uploaded documents:

.. include:: tutorial/finbidder-documents.http
   :code:

For the best effect (biggest economy) auction should have multiple bidders registered:

.. include:: tutorial/register-2nd-finbidder.http
   :code:
