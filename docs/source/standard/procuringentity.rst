.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: ProcuringEntity

.. _ProcuringEntity:

ProcuringEntity (Organizer)
===========================

Schema
------

:name:
    string, multilingual

    |ocdsDescription|
    The common name of the organization.

:identifier:
    :ref:`Identifier`

    |ocdsDescription|
    The primary identifier for this organization.

:additionalIdentifiers:
    List of :ref:`identifier` objects

:address:
    :ref:`Address`, required

:contactPoint:
    :ref:`ContactPoint`, required

:kind:
    string
    
    Type of organizer

    Possible values:
        - ``general`` - Organizer (general)
        - ``special`` - Organizer that operates in certain spheres of economic activity
        - ``other`` -  Legal persons that are not organizers in the sense of the Law, but are state, utility, public enterprises, economic partnerships or associations of enterprises in which state or public utility share is 50 percent or more

