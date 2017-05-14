import unittest
from pyactor.context import set_context, create_host, shutdown, sleep
from groupcast.monitor import Monitor
from groupcast.group import Group
from groupcast.peer import Sequencer


class SequencerTest(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

        set_context()
        self.host = create_host()

    def test_sequencer(self):
        monitor = self.host.spawn('monitor', Monitor)
        monitor.start_monitoring()

        group = self.host.spawn('group', Group)
        group.attach_monitor(monitor)
        group.init_start()

        peer0 = self.host.spawn('peer0', Sequencer)
        peer0.attach(monitor, group)

        peer0.multicast('1')
        peer0.multicast('2')

        sleep(1)

        self.assertEqual(['1', '2'], peer0.get_messages())

        self.assertEqual([], peer0.get_wait_queue())


    def tearDown(self):
        unittest.TestCase.tearDown(self)
        shutdown()

if __name__ == '__main__':
    unittest.main()