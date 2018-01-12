.. _acceleration:

Acceleration mode for sandbox
=============================

If you want to experiment with auctions, you can use acceleration mode and start your auction name with "TESTING".

Acceleration mode was developed to enable `dgfOtherAssets` procedure testing in the sandbox and to reduce time frames of this procedure. 

To enable acceleration mode you will need to:
    * add additional parameter `mode` with a value ``test``;
    * set ``quick, accelerator=1440`` as text value for `procurementMethodDetails`. This parameter will accelerate auction periods. The number 1440 shows that restrictions and time frames will be reduced in 1440 times.
    * set ``quick`` as a value for `submissionMethodDetails`. This parameter works only with ``mode = "test"`` and will speed up auction start date.

**This mode will work only in the sandbox**.

.. include:: tutorial/auction-post-acceleration.http
   :code:

Synchronization
~~~~~~~~~~~~~~~

* During normal auction synchronization via ``/auctions`` test auctions are not visible.

* To get test auctions synchronize via ``/auctions?mode=test``.

* If you synchronize via ``/auctions?mode=all``, then you will get all auctions.

* Auction mode can be set only on auction creation, it can not be set later.

Additional options
~~~~~~~~~~~~~~~~~~
* no-auction option
To enable this option: set quick(``mode:no-auction``) as a value for `submissionMethodDetails`
no-auction option allows conducting the whole procedure excluding auction stage. This means that active.auction stage will be completed based on the primary bid proposals; `auctionURL` will not be created, so auction can not be viewed.

* fast-forward option
To enable this option: set quick(``mode:fast-forward``) as a value for `submissionMethodDetails`.
fast-forward option allows skipping auction stage. This means that active.auction stage will be completed based on the primary bid proposals; although `auctionURL` will be created and auction can be viewed.
