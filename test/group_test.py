import unittest
from pyactor.context import set_context, create_host, shutdown
from groupcast.group import Group
from groupcast.monitor import Monitor


class GroupTest(unittest.TestCase):

    def setUp(self):
        set_context()
        self.host = create_host()

    def test_group(self):
        monitor = self.host.spawn('monitor', Monitor)

        group = self.host.spawn('group', Group)
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

    def tearDown(self):
        shutdown()

if __name__ == '__main__':
    unittest.main()
