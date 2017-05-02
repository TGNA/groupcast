'''
Group
Made by: Oscar Blanco and Victor Colome
'''

from datetime import datetime
from pyactor.context import interval
from random import choice


class Group():
    _tell = ['attach_printer', 'leave', 'init_start', 'remove_unannounced', 'announce', 'update_count']
    _ask = ['join', 'get_members']
    _ref = ['attach_printer', 'join', 'leave', 'get_members', 'announce', 'update_count']

    def __init__(self):
        self.peers = {}
        self.sequencer = None
        self.last_known_count = None

    def init_start(self):
        self.interval_check = interval(self.host, 1, self.proxy, 'remove_unannounced')

    def attach_printer(self, printer):
        self.printer = printer

    def join(self, peer):
        self.peers[peer] = datetime.now()
        if(len(self.peers.keys()) == 1):
            self.sequencer = peer
            print "Sequencer: ", peer.get_id()
        if self.last_known_count is None:
            count = -1
        else:
            count = self.last_known_count

        return (self.sequencer, count)

    def leave(self, peer):
        del self.peers[peer]
        if self.sequencer == peer and len(self.peers.keys()) > 0:
            self.sequencer = choice(self.peers.keys())
            self.sequencer.set_count(self.last_known_count)

            for p in self.peers.keys():
                p.attach_sequencer(self.sequencer)
            print "New sequencer: ", self.sequencer.get_id() #, "Remove peer: ", peer.get_id()

    def get_members(self):
        return self.peers.keys()

    def remove_unannounced(self, diff_time=10):
        current = datetime.now()
        for peer, last_update in self.peers.items():
            diff = current - last_update
            if diff.total_seconds() > diff_time:
                self.leave(peer)

    def announce(self, peer):
        self.peers[peer] = datetime.now()

    def update_count(self, count):
        self.last_known_count = count
