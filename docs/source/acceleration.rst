.. _acceleration:

Acceleration mode for sandbox
=============================

Acceleration mode was developed to enable `dgfOtherAssets` procedure testing in the sandbox and to reduce time frames of this procedure. 

In order to use acceleration mode you should set `quick, accelerator=1440` as text value for `procurementMethodDetails` during tender creation. The number 1440 shows that restrictions and time frames will be reduced in 1440 times. **This mode will work only in the sandbox**.

.. include:: tutorial/auction-post-acceleration.http
   :code:
