from openprocurement.auctions.dgf.tests.base import BaseAuctionWebTest
from openprocurement.auctions.core.tests.plugins.transferring.mixins import AuctionOwnershipChangeTestCaseMixin

class AuctionOwnershipChangeResourceTest(BaseAuctionWebTest,
                                         AuctionOwnershipChangeTestCaseMixin):

    def setUp(self):
        super(AuctionOwnershipChangeResourceTest, self).setUp()
        self.not_used_transfer = self.create_transfer()

def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(AuctionOwnershipChangeResourceTest))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
