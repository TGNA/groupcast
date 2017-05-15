import unittest
from pyactor.context import set_context, create_host, shutdown, sleep
from groupcast.monitor import Monitor
import sys


class MonitorTest(unittest.TestCase):

    def setUp(self):
        set_context()
        self.host = create_host()

    def test_monitor(self):
        monitor = self.host.spawn('monitor', Monitor)

        monitor.start_monitoring()

        monitor.to_print("test")
        sleep(1)
        self.assertEqual(sys.stdout.getvalue().strip(), 'test')

        monitor.print_table()
        sleep(1)
        self.assertEqual(sys.stdout.getvalue().strip(), 'test')

        monitor.stop_monitoring()

    def tearDown(self):
        shutdown()

if __name__ == '__main__':
    unittest.main()
