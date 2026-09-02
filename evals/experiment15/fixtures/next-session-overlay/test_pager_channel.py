import unittest

from alerts import create_alert


class PagerChannelTests(unittest.TestCase):
    def test_pager_is_an_accepted_channel_without_mutation(self):
        request = {"topic": "build", "channel": "pager"}
        outbox = []
        self.assertEqual(create_alert(request, outbox), {"alert": request})
        self.assertEqual(outbox, [request])
        self.assertEqual(request, {"topic": "build", "channel": "pager"})


if __name__ == "__main__":
    unittest.main()
