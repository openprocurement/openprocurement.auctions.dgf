.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Auction, Auction
.. _auction:

Auction
=======

Schema
------

:id:
   uuid, auto-generated, read-only

   Internal id of the procedure.

:date:
   date, auto-generated, read-only

   The date of the procedure creation/undoing.

:owner:
   string, auto-generated, read-only

   The entity (eMall) whom the procedure has been created by.
 
:title:
    string, multilingual, required

    Can be edited during the rectificationPeriod.
    
    * Ukrainian by default (required) - Ukrainian title
    
    * ``title_en`` (English) - English title
    
    * ``title_ru`` (Russian) - Russian title
    
    Oprionally can be mentioned in English/Russian.

   The name of the auction, displayed in listings. 

:description:
    string, multilingual, required

    Can be edited during the rectificationPeriod.
    
    |ocdsDescription|
    A description of the goods, services to be provided.
    
    * Ukrainian by default - Ukrainian decription
    
    * ``decription_en`` (English) - English decription
    
    * ``decription_ru`` (Russian) - Russian decription

:dgfDecisionID:
   string, auto-generated, read-only

   Can be edited during the rectificationPeriod.

   The number of the decision.

:dgfDecisionDate:
   :ref:`date`, required

   Can be edited during the rectificationPeriod.

   The date of the decision on the approval of the terms of sale.

:procurementMethod:
   string, auto-generated, read-only

   Purchase method. The only value is “open”.

:auctionID:
   string, auto-generated, read-only

   The auction identifier to refer auction to in "paper" documentation. 

   |ocdsDescription|
   AuctionID should always be the same as the OCID. It is included to make the flattened data structure more convenient.
   
:dgfID:
    string, required

    Can be edited during the rectificationPeriod.
    
    Identification number of the auction (also referred to as `lot`) in the XLS of Deposit Guarantee Fund.
    
:procurementMethodType:
   string, required
    
   Auction announcement. 
   Possible values:

   * ``dgfOtherAssets`` - sale of the insolvent bank property
   * ``dgfFinancialAssets`` - sale of the creditor claim right

:procurementMethodDetails:
   string, auto-generated, read-only

   Parameter that accelerates auction periods. Set quick, accelerator=1440 as text value for procurementMethodDetails for the time frames to be reduced in 1440 times.

:submissionMethod:
   string, optional

   The given value is `electronicAuction`.

:awardCriteria:
   string, optional

   Сriterion of a winner selection. The given value is `highestCost`.

:procuringEntity:
   :ref:`ProcuringEntity`, required

   Organization conducting the auction.
   

   |ocdsDescription|
   The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.

:tenderAttempts:
   integer, required

   Can be edited during the rectificationPeriod.

   The number which represents what time (from 1 up to 8) tender is taking place.

:value:
   :ref:`value`, required

   Auction starting price. Bids lower than ``value`` will be rejected.

   |ocdsDescription|
   The total estimated value of the procurement.

:guarantee:
   :ref:`Guarantee`, read-only

   The assumption of responsibility for payment of performance of some obligation if the liable party fails to perform to expectations.

:items:
   Array of :ref:`item` objects, required

   Can be edited during the rectificationPeriod (Can editing in 2 ways: each object from the array separately and the entire array together).

   List that contains single item being sold. 

   |ocdsDescription|
   The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.

:features:
   Array of :ref:`Feature` objects

   Features of auction.

:documents:
   Array of :ref:`document` objects
 
   |ocdsDescription|
   All documents and attachments related to the auction.

:dateModified:
   :ref:`date`, auto-generated, read-only

   |ocdsDescription|
   Date when the auction was last modified

:questions:
   Array of :ref:`question` objects

   Questions to ``procuringEntity`` and answers to them.

:complaints:
   Array of :ref:`complaint` objects

   Complaints to auction conditions and their resolutions.

:bids:
   Array of :ref:`bid` objects

   A list of all bids placed in the auction with information about participants, their proposals and other qualification documentation.

   |ocdsDescription|
   A list of all the companies who entered submissions for the auction.

:minimalStep:
   :ref:`value`, required

   Auction step (increment). Validation rules:

   * `amount` should be greater than `Auction.value.amount`
   * `currency` should either be absent or match `Auction.value.currency`
   * `valueAddedTaxIncluded` should either be absent or match `Auction.value.valueAddedTaxIncluded`

:awards:
   Array of :ref:`award` objects

   All qualifications (disqualifications and awards).

:contracts:
   Array of :ref:`Contract` objects

   |ocdsDescription|
   Information on contracts signed as part of a process.

:rectificationPeriod:
   :ref:`period`, auto-generated, read-only

   The period when you can edit the procedure. Duration of period 48 h.

:enquiryPeriod:
   :ref:`period`, auto-generated, read-only

   Period when questions are allowed.

   |ocdsDescription|
   The period during which enquiries may be made and will be answered.

:tenderPeriod:
   :ref:`period`, auto-generated, read-only

   Period when bids can be submitted.

   |ocdsDescription|
   The period when the auction is open for submissions. The end date is the closing date for auction submissions.

:auctionPeriod:
   :ref:`period`, required

   Period when Auction is conducted. `startDate` should be provided.

:auctionUrl:
   url, auto-generated, read-only

   A web address where auction is accessible for view.

:awardPeriod:
   :ref:`period`, auto-generated, read-only

   Awarding process period.

   |ocdsDescription|
   The date or period on which an award is anticipated to be made.

:status:
   string, required

   :`active.tendering`:
       Tendering period (tendering)
   :`active.auction`:
       Auction period (auction)
   :`active.qualification`:
       Winner qualification (qualification)
   :`active.awarded`:
       Standstill period (standstill)
   :`unsuccessful`:
       Unsuccessful auction (unsuccessful)
   :`complete`:
       Complete auction (complete)
   :`cancelled`:
       Cancelled auction (cancelled)

   Auction status.

:eligibilityCriteria:
   string, auto-generated, read-only
    
   Required for `dgfFinancialAssets` procedure.
    
   This field is multilingual: 
    
   * Ukrainian by default - До участі допускаються лише ліцензовані фінансові установи.
    
   * ``eligibilityCriteria_ru`` (Russian) - К участию допускаются только лицензированные финансовые учреждения.
    
   * ``eligibilityCriteria_en`` (English) - Only licensed financial institutions are eligible to participate.

:cancellations:
   List of :ref:`cancellation` objects.

   Contains 1 object with `active` status in case of cancelled Auction.

   The :ref:`cancellation` object describes the reason of auction cancellation and contains accompanying
   documents  if there are any.

:revisions:
   List of :ref:`revision` objects, auto-generated

   Historical changes to `Auction` object properties.

:numberOfBids:
   integer, auto-generated, read-only

   Number of offers.
