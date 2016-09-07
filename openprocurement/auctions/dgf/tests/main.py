# -*- coding: utf-8 -*-

import unittest

from openprocurement.auctions.dgf.tests import auction, award, bidder, document, tender, question, complaint
#from openprocurement.auctions.dgf.tests import migration


def suite():
    suite = unittest.TestSuite()
    suite.addTest(auction.suite())
    suite.addTest(award.suite())
    suite.addTest(bidder.suite())
    suite.addTest(complaint.suite())
    suite.addTest(document.suite())
    suite.addTest(migration.suite())
    suite.addTest(question.suite())
    suite.addTest(tender.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
