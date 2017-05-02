'''
Peer
Made by: Oscar Blanco and Victor Colome
'''


from Queue import PriorityQueue
from pyactor.context import interval
from pyactor.exceptions import TimeoutError

import heapq

class UniquePriorityQueue(PriorityQueue):
    def _init(self, maxsize):
        PriorityQueue._init(self, maxsize)
        self.priorities = set()

    def _put(self, item, heappush=heapq.heappush):
        if item[0] not in self.priorities:
            self.priorities.add(item[0])
            PriorityQueue._put(self, item, heappush)

    def _get(self, heappop=heapq.heappop):
        item = PriorityQueue._get(self, heappop)
        self.priorities.remove(item[0])
        return item


class Peer:
    _tell = ['attach_printer', 'attach_group', 'attach_sequencer', 'multicast', 'receive', 'process_msg', 'check_queue', 'announce_me', 'set_count']
    _ask = ['get_count', 'is_sequencer', 'get_id', 'get_messages', 'get_wait_queue']
    _ref = ['attach_printer', 'attach_group', 'attach_sequencer', 'get_count']

    def __init__(self):
        self.messages = []
        self.wait_queue = UniquePriorityQueue()
        self.count = -1
        self.last_count_processed = -1

    def attach_printer(self, printer):
        self.printer = printer

    def attach_group(self, group):
        self.group = group
        self.sequencer, self.last_count_processed = self.group.join(self)
        self.interval = interval(self.host, 3, self.proxy, 'announce_me')

    def attach_sequencer(self, sequencer):
        self.sequencer = sequencer

    def get_id(self):
        return self.id

    def multicast(self, msg):
        priority = self.sequencer.get_count()
        for peer in self.group.get_members():
            peer.receive(priority, msg)
        # self.printer.to_print(str(self.id) + " msg: " + msg + " priority: " + str(priority))

    def receive(self, priority, msg):
        self.printer.to_print(self.id + " receive " + str(self.last_count_processed) + " " + str(priority-1))
        if(self.last_count_processed == (priority - 1)):
            self.process_msg(priority, msg)
            while not self.wait_queue.empty():
                priority, msg = self.wait_queue.get()
                if (self.last_count_processed == (priority - 1)):
                    self.process_msg(priority, msg)
                else:
                    self.wait_queue.put((priority, msg))
                    return
        else:
            self.wait_queue.put((priority, msg))
        # self.wait_queue.put((priority, msg))
        # self.check_queue()

    def process_msg(self, priority, msg):
        #self.printer.to_print(self.id + " process_msg " + str(priority) + " " + msg)
        self.last_count_processed = priority
        self.messages.append(msg)

    def get_messages(self):
        return self.messages

    def get_wait_queue(self):
        return sorted(self.wait_queue.queue, key=lambda t: t[0])

    def announce_me(self):
        self.group.announce(self.proxy)

    def get_count(self):
        self.count += 1
        self.group.update_count(self.count)
        return self.count

    def set_count(self, count):
        self.count = count
