.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Lot

.. _Lot:

Lot
===

Schema
------

:id:
    string, auto-generated

:title:
   string, multilingual

   The name of the auction lot.

:description:
   string, multilingual

   Detailed description of auction lot.

:value:
   :ref:`value`, required

   Total available auction lot budget. Bids greater then ``value`` will be rejected.

:guarantee:
    :ref:`Guarantee`

    Bid guarantee

:minimalStep:
   :ref:`value`, required

   The minimal step of auction (reduction). Validation rules:

   * `amount` should be less then `Lot.value.amount`
   * `currency` should either be absent or match `Lot.value.currency`
   * `valueAddedTaxIncluded` should either be absent or match `Lot.value.valueAddedTaxIncluded`

:auctionPeriod:
   :ref:`period`, read-only

   Period when Auction is conducted.

:auctionUrl:
    url

    A web address for view auction.

:status:
   string

   :`active`:
       Active auction lot (active)
   :`unsuccessful`:
       Unsuccessful auction lot (unsuccessful)
   :`complete`:
       Complete auction lot (complete)
   :`cancelled`:
       Cancelled auction lot (cancelled)

   Status of the Lot.
