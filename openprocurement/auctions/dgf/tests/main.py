# -*- coding: utf-8 -*-

import unittest

from openprocurement.auctions.dgf.tests import (
    auction, award, bidder, cancellation, chronograph, complaint, contract, document, lot, migration, tender, question
)


def suite():
    tests = unittest.TestSuite()
    tests.addTest(auction.suite())
    tests.addTest(award.suite())
    tests.addTest(bidder.suite())
    tests.addTest(cancellation.suite())
    tests.addTest(chronograph.suite())
    tests.addTest(complaint.suite())
    tests.addTest(contract.suite())
    tests.addTest(document.suite())
    tests.addTest(lot.suite())
    tests.addTest(migration.suite())
    tests.addTest(question.suite())
    tests.addTest(tender.suite())
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
