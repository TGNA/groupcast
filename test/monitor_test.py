import unittest
from pyactor.context import set_context, create_host, shutdown, sleep
from groupcast.monitor import Monitor
import sys
from StringIO import StringIO


class MonitorTest(unittest.TestCase):

    def setUp(self):
        set_context()
        self.host = create_host()
        self.old_stdout = sys.stdout

    def test_monitor(self):
        monitor = self.host.spawn('monitor', Monitor)

        monitor.start_monitoring()

        sys.stdout = StringIO()
        monitor.to_print("test")
        sleep(1)
        self.assertEqual(sys.stdout.getvalue().strip(), 'test')


        sleep(1)
        sys.stdout = StringIO()
        monitor.monitor('peer1', '1')
        monitor.print_table()
        sleep(1)
        self.assertEqual(sys.stdout.getvalue().strip(), 'peer1: 1')

        monitor.stop_monitoring()

    def tearDown(self):
        shutdown()
        sys.stdout = self.old_stdout

if __name__ == '__main__':
    unittest.main()
