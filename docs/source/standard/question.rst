.. . Kicking page rebuild 2014-10-30 17:00:08

.. index:: Question, Answer, Author
.. _question:

Question
========

Schema
------

:id:
    UID, auto-generated

:author:
    :ref:`Organization`, required

    Who is asking a question (contactPoint - person, identification - organization that person represents).

:title:
    string, required

    Title of the question.

:description:
    string

    Description of the question.

:date:
    string, :ref:`date`, auto-generated

    Date of posting.

:answer:
    string

    Answer for the question.

:questionOf:
    string

    Possible values are:

    * `auction`
    * `item`
..    * `lot`

:relatedItem:
    string

    ID of related :ref:`item`.

..    ID of related :ref:`lot` or :ref:`item`.

