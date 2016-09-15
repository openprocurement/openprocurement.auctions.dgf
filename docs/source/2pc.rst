.. _2pc:

2 Phase Commit
==============

.. _auction-2pc:

Creating auction with 2 Phase Commit
------------------------------------

Let's create auction in `draft` status:

.. include:: tutorial/auction-post-2pc.http
   :code:

And now let's switch to `active.tendering` status:

.. include:: tutorial/auction-patch-2pc.http
   :code:
