import unittest
from pyactor.context import set_context, create_host, shutdown, sleep
from groupcast.monitor import Monitor
from groupcast.group import Group
from groupcast.peer import Sequencer


class SequencerTest(unittest.TestCase):
    def test_sequencer(self):
        try:
            set_context()
        except:
            pass

        try:
            host = create_host()
        except:
            shutdown()
            host = create_host()

        monitor = host.spawn('monitor', Monitor)
        monitor.start_monitoring()

        group = host.spawn('group', Group)
        group.attach_monitor(monitor)
        group.init_start()

        peer0 = host.spawn('peer0', Sequencer)
        peer0.attach(monitor, group)

        self.assertEqual(('local://local:6666/peer0', False), peer0.get_sequencer_url())

        peer0.multicast('1')
        peer0.multicast('2')

        sleep(1)

        self.assertEqual(['1', '2'], peer0.get_messages())

        self.assertEqual([], peer0.get_wait_queue())

        peer1 = host.spawn('peer1', Sequencer)
        peer1.attach(monitor, group)

        sleep(1)
        peer0.leave_group()
        sleep(1)

        peer2 = host.spawn('peer2', Sequencer)
        peer2.attach(monitor, group)
        sleep(0.5)
        peer3 = host.spawn('peer3', Sequencer)
        peer3.attach(monitor, group)

        sleep(2)

        self.assertEqual(('local://local:6666/peer2', False), peer1.get_sequencer_url())
        self.assertEqual(('local://local:6666/peer2', False), peer2.get_sequencer_url())
        self.assertEqual(('local://local:6666/peer2', False), peer3.get_sequencer_url())

        monitor.stop_monitoring()

        shutdown()

if __name__ == '__main__':
    unittest.main()
