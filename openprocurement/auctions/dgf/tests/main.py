# -*- coding: utf-8 -*-

import unittest

from openprocurement.auctions.dgf.tests.other import (auction as other_auction,
    award as other_award, bidder as other_bidder, document as other_document,
    tender as other_tender, question as other_question, complaint as other_complaint)
from openprocurement.auctions.dgf.tests.financial import (auction as financial_auction,
    award as financial_award, bidder as financial_bidder, document as financial_document,
    tender as financial_tender, question as financial_question, complaint as financial_complaint)
#from openprocurement.auctions.dgf.tests import migration


def suite():
    suite = unittest.TestSuite()
    suite.addTest(other_auction.suite())
    suite.addTest(other_award.suite())
    suite.addTest(other_bidder.suite())
    suite.addTest(other_complaint.suite())
    suite.addTest(other_document.suite())
    suite.addTest(other_migration.suite())
    suite.addTest(other_question.suite())
    suite.addTest(other_tender.suite())
    suite.addTest(financial_auction.suite())
    suite.addTest(financial_award.suite())
    suite.addTest(financial_bidder.suite())
    suite.addTest(financial_complaint.suite())
    suite.addTest(financial_document.suite())
    suite.addTest(financial_migration.suite())
    suite.addTest(financial_question.suite())
    suite.addTest(financial_tender.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
`