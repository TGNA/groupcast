import unittest
from pyactor.context import set_context, create_host, shutdown
from groupcast.monitor import Monitor


class MonitorTest(unittest.TestCase):

    def setUp(self):
        set_context()
        self.host = create_host()

    def test_monitor(self):
        monitor = self.host.spawn('monitor', Monitor)

        monitor.to_print("test")


    def tearDown(self):
        shutdown()

if __name__ == '__main__':
    unittest.main()
