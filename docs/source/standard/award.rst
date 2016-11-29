.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Award
.. _award:

Award
=====

Schema
------

:id:
    string, auto-generated, read-only
    
    |ocdsDescription|
    Identifier for this award.
    
:bid_id:
    string, auto-generated, read-only

    The ID of a bid that the award relates to.
    
:title:
    string, multilingual
    
    |ocdsDescription|
    Award title.
    
:description:
    string, multilingual
    
    |ocdsDescription|
    Award description.
    
:status:
    string
    
    |ocdsDescription|
    The current status of the award drawn from the `awardStatus` codelist.

    Possible values are:

    * `pending.verification` - the procedure awaits the auction protocol to be uploaded
    * `pending.payment` - the procedure awaits the payment to be made
    * `unsuccessful` - the award has been rejected by the qualification committee (bank)
    * `active` - the auction is awarded to the bidder from the `bid_id`
    * `pending.waiting` - the second bidder awaits the first bidder to be disqualified
    * `cancelled` - the second bidder does not want to wait for the first bidder to be disqualified

:verificationPeriod:
    :ref:`period`
    
    The period of uploading (for the auction winner) and verification (for the bank) of the auction protocol
    
:paymentPeriod:
    :ref:`period`

    The period given to the winner of the auction to make a payment
    
:signingPeriod:
    :ref:`period`

    The period for the contract to be activated in the system (by the bank)
    
:date:
    string, :ref:`Date`, auto-generated, read-only
    
    |ocdsDescription|
    The date of the contract award.
    
:value:
    `Value` object, auto-generated, read-only
    
    |ocdsDescription|
    The total value of this award.
    
:suppliers:
    List of :ref:`Organization` objects, auto-generated, read-only
    
    |ocdsDescription|
    The suppliers awarded with this award.
    
:items:
    List of :ref:`Item` objects, auto-generated, read-only
    
    |ocdsDescription|
    The goods and services awarded in this award, broken into line items wherever possible. Items should not be duplicated, but the quantity should be specified instead. 
    
:documents:
    List of :ref:`Document` objects
    
    |ocdsDescription|
    All documents and attachments related to the award, including any notices. 
    
:complaints:
    List of :ref:`Complaint` objects

:complaintPeriod:
    :ref:`period`

    The time frame when complaints can be submitted.

.. :lotID:
    string

    ID of related :ref:`lot`.
