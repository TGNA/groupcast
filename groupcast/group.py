from datetime import datetime
from pyactor.context import interval
from random import choice
from groupcast.peer import Peer


class Group(object):
    _tell = ['init_start', 'attach_monitor', 'leave', 'remove_unannounced', 'announce', 'update_count']
    _ask = ['join', 'get_members']
    _ref = ['attach_monitor', 'join', 'leave', 'get_members', 'announce']

    def __init__(self):
        self.peers = {}
        self.sequencer_url = None
        self.last_known_count = None

    def init_start(self):
        self.interval_check = interval(self.host, 1, self.proxy, 'remove_unannounced')

    def attach_monitor(self, monitor):
        self.monitor = monitor

    def join(self, peer):
        self.peers[peer] = datetime.now()
        if(len(self.peers.keys()) == 1):
            self.sequencer_url = peer
            self.monitor.to_print("New sequencer: "+self.sequencer_url+"\n")

        if self.last_known_count is None:
            count = -1
        else:
            count = self.last_known_count

        return (self.sequencer_url, count)

    def leave(self, peer):
        del self.peers[peer]
        if self.sequencer_url == peer and len(self.peers.keys()) > 0:
            self.sequencer_url = choice(self.peers.keys())
            self.monitor.to_print("New sequencer: "+self.sequencer_url+"\n")
            sequencer = self.host.lookup_url(self.sequencer_url, 'Peer', 'groupcast.peer')
            sequencer.set_count(self.last_known_count)

            for peer_url in self.peers.keys():
                p = self.host.lookup_url(peer_url, 'Peer', 'groupcast.peer')
                p.attach_sequencer(self.sequencer_url)

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
