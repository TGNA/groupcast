'''
Group
Made by: Oscar Blanco and Victor Colome
'''


class Group():
    _tell = ['join', 'leave', 'init_start', 'remove_unannounced', 'announce']
    _ask = ['get_members']
    _ref = ['join', 'leave', 'get_members', 'announce']

    def __init__(self):
        self.peers = {}

    def init_start(self):
        self.interval_check = interval(self.host, 1, self.proxy, 'remove_unannounced')

    def join(self, peer):
        self.peers[peer] = datetime.now()

    def leave(self, peer):
        self.peers.pop(peer, None)
        if peer.is_sequencer():
            newSeq = choice(self.peers.keys())
            newSeq.set_counter(peer.get_counter()-1)
            for p in self.peers:
                p.attach_sequencer(newSeq)

    def get_members(self):
        return list(self.peers)

    def remove_unannounced(self, diff_time=10):
        current = datetime.now()
        for peer, last_update in self.peers.items():
            diff = current - last_update
            if diff.total_seconds() > diff_time:
                self.leave(peer)

    def announce(self, peer):
        self.peers[peer] = datetime.now()
