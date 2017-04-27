'''
Peer
Made by: Oscar Blanco and Victor Colome
'''

from Queue import PriorityQueue

class Peer(): # Heredar de Sequencer o juntarlos en 1
    _tell = ['attach_group', 'attach_sequencer', 'multicast', 'receive', 'process_msg', 'check_queue', 'get_queue', 'init_start', 'announce_me']
    _ask = ['']
    _ref = ['attach_group', 'attach_sequencer']

    def __init__(self):
        self.priority_queue = PriorityQueue()
        self.wait_queue = PriorityQueue()

    def init_start(self):
        self.interval = interval(self.host, 3, self.proxy, 'announce_me')

    def attach_group(self, group):
        self.group = group

    def attach_sequencer(self, sequencer):
        self.sequencer = sequencer

    def multicast(self, msg):
        priority = self.sequencer.get_count()
        peers = set(self.group.get_members()) - set([self])  # Creo que no hace falta
        for peer in peers:
            peer.receive(priority, msg)

    def receive(self, priority, msg):
        num = priority_queue.qsize()
        if priority == num + 1:
            self.process_msg(priority, msg)
            self.check_queue(priority)
        else:
            self.wait_queue.put((priority, msg))

    def process_msg(self, priority, msg):
        self.priority_queue.put((priority, msg))

    def check_queue(self, priority):
        for tuple in self.wait_queue.queue:
            priority = priority + 1
            if tuple[0] == priority:
                self.wait_queue.get()
                self.process_msg(tuple[0], tuple[1])

    def get_queue(self):
        aux = []
        for tuple in self.priority_queue.queue:
            aux.append(tuple[1])
        return aux

    def announce_me(self):
        self.group.announce(self.proxy)