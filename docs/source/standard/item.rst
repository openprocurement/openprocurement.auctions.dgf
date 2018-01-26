.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Item, Parameter, Classification, CAV, Unit

.. _Item:

Item
====

Schema
------

:id:
    string, auto-generated

:description:
    string, multilingual, required

    |ocdsDescription|
    A description of the goods, services to be provided.
    
    Brief description of property (for ``dgfOtherAssets``) or asset(s) (for ``dgfFinancialAssets``).
    
:classification:
    :ref:`Classification`

    |ocdsDescription|
    The primary classification for the item. See the
    `itemClassificationScheme` to identify preferred classification lists,
    including CAV and GSIN.

    It is required for `classification.scheme` to be `CAV`. The
    `classification.id` should be valid CAV code.

:schema_properties:
    :ref:`SchemaProperties`
    
    |ocdsDescription| 
    A detailed specification of the fields and data structures 
    to use when publishing contracting data.

:additionalClassifications:
    List of :ref:`Classification` objects

    |ocdsDescription|
    An array of additional classifications for the item. See the
    `itemClassificationScheme` codelist for common options to use in OCDS. 
    This may also be used to present codes from an internal classification
    scheme.

    It is required to have at least one item with `ДКПП` as `scheme`.

:unit:
    :ref:`Unit`

    |ocdsDescription| 
    Description of the unit which the good comes in e.g.  hours, kilograms. 
    Made up of a unit name, and the value of a single unit.

:quantity:
    integer

    |ocdsDescription|
    The number of units required

:address:
    :ref:`Address`

    Address, where property (for ``dgfOtherAssets``) or asset(s) (for ``dgfFinancialAssets``) is located.

:location:
    dictionary

    Geographical coordinates of the location. Element consists of the following items:

    :latitude:
        string, required
    :longitude:
        string, required
    :elevation:
        string, optional, usually not used

    `location` usually takes precedence over `address` if both are present.

.. :relatedLot:
    string

    ID of related :ref:`lot`.


.. _Classification:

Classification
==============

Schema
------

:scheme:
    string

    |ocdsDescription|
    A classification should be drawn from an existing scheme or list of
    codes.  This field is used to indicate the scheme/codelist from which
    the classification is drawn.  For line item classifications, this value
    should represent a known Item Classification Scheme wherever possible.

:id:
    string

    |ocdsDescription|
    The classification code drawn from the selected scheme.

:description:
    string

    |ocdsDescription|
    A textual description or title for the code.

:uri:
    uri

    |ocdsDescription|
    A URI to identify the code. In the event individual URIs are not
    available for items in the identifier scheme this value should be left
    blank.

.. _Unit:

Unit
====

Schema
------

:code:
    string, required

    UN/CEFACT Recommendation 20 unit code.

:name:
    string

    |ocdsDescription|
    Name of the unit

.. _SchemaProperties:

SchemaProperties
================

Schema
------

:code:
    string, required, should match classification.id
    
:version:
    string, optional, identifies the scheme version 
    
    If not specified, the latest version will be used.
    
:properties:
    dictionary, match the version and code used
    
    The detailed description is given here: http://schemas.api-docs.ea.openprocurement.io/en/latest/
