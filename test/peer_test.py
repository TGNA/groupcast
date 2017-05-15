import unittest
from pyactor.context import set_context, create_host, shutdown, sleep
from groupcast.monitor import Monitor
from groupcast.group import Group
from groupcast.peer import Lamport, Peer, Sequencer


class PeerTest(unittest.TestCase):

    def setUp(self):
        set_context()
        self.host = create_host()

    def test_peer(self):
        p = Peer()
        self.assertRaises(NotImplementedError, p.get_wait_queue)
        self.assertRaises(NotImplementedError, p.multicast)
        self.assertRaises(NotImplementedError, p.receive)

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

    def test_sequencer(self):
        monitor = self.host.spawn('monitor', Monitor)
        monitor.start_monitoring()

        group = self.host.spawn('group', Group)
        group.attach_monitor(monitor)
        group.init_start()

        peer0 = self.host.spawn('peer0', Sequencer)
        peer0.attach(monitor, group)

        self.assertEqual(('local://local:6666/peer0', False), peer0.get_sequencer_url())

        peer0.multicast('1')
        peer0.multicast('2')

        sleep(1)

        self.assertEqual(['1', '2'], peer0.get_messages())

        self.assertEqual([], peer0.get_wait_queue())

        peer1 = self.host.spawn('peer1', Sequencer)
        peer1.attach(monitor, group)

        sleep(1)
        peer0.leave_group()
        sleep(1)

        peer2 = self.host.spawn('peer2', Sequencer)
        peer2.attach(monitor, group)
        sleep(0.5)
        peer3 = self.host.spawn('peer3', Sequencer)
        peer3.attach(monitor, group)

        sleep(2)

        self.assertEqual(('local://local:6666/peer2', False), peer1.get_sequencer_url())
        self.assertEqual(('local://local:6666/peer2', False), peer2.get_sequencer_url())
        self.assertEqual(('local://local:6666/peer2', False), peer3.get_sequencer_url())

        monitor.stop_monitoring()

    def tearDown(self):
        shutdown()

if __name__ == '__main__':
    unittest.main()
