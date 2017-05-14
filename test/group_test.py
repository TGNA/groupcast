import unittest
from pyactor.context import set_context, create_host, shutdown, sleep
from groupcast.group import Group
from groupcast.monitor import Monitor


class GroupTest(unittest.TestCase):

    def test_group(self):
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

        group = host.spawn('group', Group)
        group.attach_monitor(monitor)
        group.init_start()

        group.announce('1')
        group.announce('2')
        group.announce('3')

        self.assertEqual(set(['1', '2', '3']), set(group.get_members()))

        group.leave('2')

        self.assertEqual(set(['1', '3']), set(group.get_members()))

        group.remove_unannounced(0)

        self.assertEqual([], group.get_members())

        shutdown()

if __name__ == '__main__':
    unittest.main()
