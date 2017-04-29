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
        self.last_known_count = 0

    def init_start(self):
        self.interval_check = interval(self.host, 1, self.proxy, 'remove_unannounced')

    def attach_printer(self, printer):
        self.printer = printer

    def join(self, peer):
        self.peers[peer] = datetime.now()
        if(len(self.peers.keys()) == 1):
            self.sequencer = peer
        return self.sequencer

    def leave(self, peer):
        self.peers.pop(peer)
        if self.sequencer == peer and len(self.peers.values()) > 0:
            peer = choice(self.peers.keys())
            peer.set_count(self.last_known_count)

            for p in self.peers.keys():
                p.attach_sequencer(peer)

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
