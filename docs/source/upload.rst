.. _upload:

Documents Uploading
===================

All of the document uploading API endpoints follow the same set of rules.

Upload document with registration
---------------------------------

#. :ref:`Register document upload in document service <documentservice:register-document-upload>`.

#. Add document in API:

    .. include:: tutorial/upload-auction-notice.http
        :code:

#. :ref:`Upload document in document service <documentservice:upload-document>`.

Upload document without registration
------------------------------------

#. :ref:`Upload document without registration <documentservice:upload-document-w-o-registration>`.

#. Add document in API:

    .. include:: tutorial/upload-auction-notice.http
        :code:
