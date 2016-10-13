.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Cancellation
.. _cancellation:

Cancellation
============

Schema
------

:id:
    UID, auto-generated

:reason:
    string, multilingual, required

    The reason, why auction is being cancelled.

:status:
    string

    Possible values are:
     :`pending`:
       Default. The request is being prepared.
     :`active`:
       Cancellation activated.

:documents:
    List of :ref:`Document` objects

    Documents accompanying the Cancellation: Protocol of Auction Committee
    with decision to cancel the Auction.

:date:
    string, :ref:`date`

    Cancellation date.

:cancellationOf:
    string

    Possible values are:

    * `auction`
..    * `lot`

.. :relatedLot:
    string

    ID of related :ref:`lot`.
