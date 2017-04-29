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

    def get_members(self):
        return list(self.peers)

    def remove_unannounced(self, diff_time=10):
        current = datetime.now()
        aux_dict = {}
        for peer, last_update in self.peers.items():
            diff = current - last_update
            if diff.total_seconds() <= diff_time:
                aux_dict[peer] = last_update
        self.peers = aux_dict

    def announce(self, peer):
        self.peers[peer] = datetime.now()