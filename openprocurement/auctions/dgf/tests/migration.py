# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.migration import migrate_data, get_db_schema_version, SCHEMA_VERSION
from openprocurement.auctions.dgf.tests.base import BaseWebTest


class MigrateTest(BaseWebTest):

    def test_migrate(self):
        self.assertEqual(get_db_schema_version(self.db), SCHEMA_VERSION)
        migrate_data(self.db, 1)
        self.assertEqual(get_db_schema_version(self.db), SCHEMA_VERSION)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MigrateTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
