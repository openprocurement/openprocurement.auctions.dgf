.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Prolongation
.. _Prolongation:

Prolongation
========

Schema
------

:id:
    UID, auto-generated

    |ocdsDescription|
    The identifier for this prolongation.

:dateCreated:
    string, auto-generated, :ref:`date`

    |ocdsDescription|
    The date when :ref:`Prolongation` was created.

:decisionID:
    string, required

    |ocdsDescription|
    Id of document, that allows prolongation.

:status:
    string, required

    |ocdsDescription|
    The current status of prolongation.

    Possible values are:

    * `draft` - this prolongation has been proposed, but is not yet in force.
      It may be awaiting activation.
    * `applied` - this prolongation has been applied, and is now legally
      in force.

:description:
    string, required

    |ocdsDescription|
    Prolongation description. Minimal length - 10 letters.

:datePublished:
    string, required, :ref:`date`

    |ocdsDescription|
    Date, when document, that caused this prolongation, came in force.

:documents:
    List of :ref:`Document` objects

    |ocdsDescription|
    All documents and attachments related to the prolongation,
    including any notices.

:reason:
    string, required

    |ocdsDescription|
    Reason, that caused prolongation.

    Possible values are:

    * `dgfPaymentImpossibility` - Prolongation was caused by payment
      impossibility of buyer.
    * `dgfLackOfDocuments` - Prolongation was caused by lack of documents.
    * `dgfLegalObstacles` - Prolongation was caused by some legal obstacles.
    * `other` - Some other causes.
