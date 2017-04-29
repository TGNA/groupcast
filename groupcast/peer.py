'''
Peer
Made by: Oscar Blanco and Victor Colome
'''


from Queue import PriorityQueue
from pyactor.context import interval
from pyactor.exceptions import TimeoutError


class Peer():
    _tell = ['attach_printer', 'attach_group', 'attach_sequencer', 'multicast', 'receive', 'process_msg', 'check_queue', 'announce_me', 'set_count']
    _ask = ['get_count', 'is_sequencer', 'get_id', 'get_queue']
    _ref = ['attach_printer', 'attach_group', 'attach_sequencer', 'get_count']

    def __init__(self):
        self.priority_queue = PriorityQueue()
        self.wait_queue = PriorityQueue()
        self.count = 0

    def attach_printer(self, printer):
        self.printer = printer

    def attach_group(self, group):
        self.group = group
        self.sequencer = self.group.join(self)
        self.interval = interval(self.host, 3, self.proxy, 'announce_me')

    def attach_sequencer(self, sequencer):
        self.sequencer = sequencer

    def get_id(self):
        return self.id

    def multicast(self, msg):
        priority = self.sequencer.get_count()

        for peer in self.group.get_members():
            peer.receive(priority, msg)

    def receive(self, priority, msg):
        num = self.priority_queue.qsize()
        if priority == num + 1:
            self.process_msg(priority, msg)
            self.check_queue(priority)
        else:
            self.wait_queue.put((priority, msg))

    def process_msg(self, priority, msg):
        self.priority_queue.put((priority, msg))

    def check_queue(self, priority):
        for tup in self.wait_queue.queue:
            priority += 1
            if tup[0] == priority:
                self.wait_queue.get()
                self.process_msg(tup[0], tup[1])

    def get_queue(self):
        return [tup[1] for tup in self.priority_queue.queue]

    def announce_me(self):
        self.group.announce(self.proxy)

    def get_count(self):
        self.count += 1
        self.group.update_count(self.count)
        return self.count

    def set_count(self, count):
        self.count = count
