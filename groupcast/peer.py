'''
Peer
Made by: Oscar Blanco and Victor Colome
'''


from Queue import PriorityQueue
from pyactor.context import interval


class Peer:
    _tell = ['attach', 'attach_printer', 'attach_group', 'attach_sequencer', 'leave_group', 'announce_me']
    _ask = ['get_id', 'get_messages', 'get_wait_queue']
    _ref = ['attach', 'attach_printer', 'attach_group']

    def __init__(self):
        self.messages = []
        self.wait_queue = PriorityQueue()

    def attach(self, printer, group):
        self.attach_printer(printer)
        self.attach_group(group)

    def attach_printer(self, printer):
        self.printer = printer

    def attach_group(self, group):
        self.group = group
        sequencer_url, self.last_count_processed = self.group.join(self.url)
        self.sequencer = self.host.lookup_url(sequencer_url, Peer)
        self.interval_announce = interval(self.host, 3, self.proxy, 'announce_me')

    def attach_sequencer(self, sequencer_url):
        while True:
            try:
                self.sequencer = self.host.lookup_url(sequencer_url, Peer)
            except Exception:
                continue
            break

    def get_id(self):
        return self.id

    def leave_group(self):
        self.printer.to_print("Leave: "+self.url)
        self.interval_announce.set()
        self.group.leave(self.url)

    def get_messages(self):
        return self.messages

    def get_wait_queue(self):
        return sorted(self.wait_queue.queue, key=lambda t: t[0])

    def announce_me(self):
        self.group.announce(self.url)


class Sequencer(Peer):
    _tell = Peer._tell + ['multicast', 'receive', 'process_msg', 'set_count', 'send_multicast']
    _ask = Peer._ask + ['get_count']

    def __init__(self):
        Peer.__init__(self)
        self.count = -1
        self.last_count_processed = -1

    def multicast(self, msg):
        future = self.sequencer.get_count(future = True)
        future.msg = msg
        future.add_callback('send_multicast')

    def send_multicast(self, future):
        priority = future.result()
        for peer_url in self.group.get_members():
            peer = self.host.lookup_url(peer_url, Peer)
            peer.receive(priority, future.msg)

    def receive(self, priority, msg):
        if self.last_count_processed == (priority - 1):
            self.process_msg(priority, msg)
            while not self.wait_queue.empty():
                priority, msg = self.wait_queue.get()
                if self.last_count_processed == (priority - 1):
                    self.process_msg(priority, msg)
                else:
                    self.wait_queue.put((priority, msg))
                    break
        else:
            self.wait_queue.put((priority, msg))

    def process_msg(self, priority, msg):
        self.last_count_processed = priority
        self.messages.append(msg)

    def get_count(self):
        self.count += 1
        self.group.update_count(self.count)
        return self.count

    def set_count(self, count):
        self.count = count


class Lamport(Peer):
    _tell = Peer._tell + []
    _ask = Peer._ask + []
    _ref = Peer._ref + []

    def __init__(self):
        Peer.__init__(self)
