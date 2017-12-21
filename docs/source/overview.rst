Overview
========

openprocurement.auctions.dgf contains documentaion for Deposit Guarantee Fund auctions.

There are two procedures:
 
 * dgfOtherAssets - sale of the insolvent bank property.
 
 * dgfFinancialAssets - sale of the creditor claim right.


Features
--------

* No need to specify enquiries period (there is no *active.enquiries* status), since it overlaps with *active.tendering* period.
* Procedure can be switched from *draft* status to *active.tendering*.
* During *active.tendering* period participants can ask questions, submit proposals, and upload documents.
* The only date Organizer has to provide is *Tender.auctionPeriod.startDate*, the rest will be calculated automatically.
* Organizer can't edit procedure's significant properties (*Auction.value*, etc.).
* There is obligatory participant qualification (*Bid.selfQualified*) via guarantee payment.
* The only currency (*Value.currency*) for this procedure is hryvnia (UAH).

Conventions
-----------

API accepts `JSON <http://json.org/>`_ or form-encoded content in
requests.  It returns JSON content in all of its responses, including
errors.  Only the UTF-8 character encoding is supported for both requests
and responses.

All API POST and PUT requests expect a top-level object with a single
element in it named `data`.  Successful responses will mirror this format. 
The data element should itself be an object, containing the parameters for
the request.  In the case of creating a new auction, these are the fields we
want to set on the auction itself.

If the request was successful, we will get a response code of `201`
indicating the object was created.  That response will have a data field at
its top level, which will contain complete information on the new auction,
including its ID.

If something went wrong during the request, we'll get a different status
code and the JSON returned will have an `errors` field at the top level
containing a list of problems.  We look at the first one and print out its
message.

Main responsibilities
---------------------

Project status
--------------

The project has beta status.

The source repository for this project is on GitHub: https://github.com/openprocurement/openprocurement.auctions.dgf

You can leave feedback by raising a new issue on the `issue tracker
<https://github.com/openprocurement/openprocurement.auctions.dgf/issues>`_ (GitHub
registration necessary).  

Documentation of related packages
---------------------------------

* `OpenProcurement API <http://api-docs.openprocurement.org/en/latest/>`_

API stability
-------------

API is relatively stable. The changes in the API are communicated via `Open Procurement API
<https://groups.google.com/group/open-procurement-api>`_ maillist.

Change log
----------

0.1
~~~

Released: not released


Next steps
----------
You might find it helpful to look at the :ref:`tutorial`.
