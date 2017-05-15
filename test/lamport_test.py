import unittest
from pyactor.context import set_context, create_host, shutdown, sleep
from groupcast.monitor import Monitor
from groupcast.group import Group
from groupcast.peer import Lamport


class LamportTest(unittest.TestCase):

    def setUp(self):
        set_context()
        self.host = create_host()

    def test_lamport(self):
        monitor = self.host.spawn('monitor', Monitor)
        monitor.start_monitoring()

        group = self.host.spawn('group', Group)
        group.attach_monitor(monitor)
        group.init_start()

        peer0 = self.host.spawn('peer0', Lamport)
        peer0.attach(monitor, group)

        sleep(0.5)
        peer0.multicast('1')
        peer0.multicast('2')

        sleep(1)

        self.assertEqual(['1', '2'], peer0.get_messages())

        self.assertEqual([], peer0.get_wait_queue())

        peer1 = self.host.spawn('peer1', Lamport)
        peer1.attach(monitor, group)

        sleep(1)
        peer0.leave_group()
        sleep(1)

        peer2 = self.host.spawn('peer2', Lamport)
        peer2.attach(monitor, group)
        sleep(0.5)
        peer3 = self.host.spawn('peer3', Lamport)
        peer3.attach(monitor, group)

        monitor.stop_monitoring()

    def tearDown(self):
        shutdown()

if __name__ == '__main__':
    unittest.main()
