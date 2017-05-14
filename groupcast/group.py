from datetime import datetime
from pyactor.context import interval


class Group(object):
    _tell = ['init_start', 'attach_monitor', 'leave', 'remove_unannounced',
             'announce']
    _ask = ['get_members']
    _ref = ['attach_monitor']

    def __init__(self):
        self.peers = {}

    def init_start(self):
        self.interval_check = interval(self.host, 1, self.proxy,
                                       'remove_unannounced')

    def attach_monitor(self, monitor):
        self.monitor = monitor

    def get_members(self):
        return self.peers.keys()

    def remove_unannounced(self, diff_time=4):
        current = datetime.now()
        for peer, last_update in self.peers.items():
            diff = current - last_update
            if diff.total_seconds() > diff_time:
                self.leave(peer)

    def announce(self, peer):
        self.peers[peer] = datetime.now()

    def leave(self, peer):
        del self.peers[peer]
        self.monitor.to_print("Leave: " + peer + "\n")
