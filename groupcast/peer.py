from Queue import PriorityQueue
from pyactor.context import interval, sleep


class Peer(object):
    _tell = ['attach', 'attach_monitor', 'attach_group', 'attach_sequencer', 'leave_group', 'announce_me', 'set_count']
    _ask = ['get_id', 'get_messages', 'get_wait_queue', 'get_count']
    _ref = ['attach', 'attach_monitor', 'attach_group']

    def __init__(self):
        self.messages = []
        self.wait_queue = PriorityQueue()
        self.count = -1

    def attach(self, monitor, group):
        self.attach_monitor(monitor)
        self.attach_group(group)

    def attach_monitor(self, monitor):
        self.monitor = monitor

    def attach_group(self, group):
        self.group = group
        sequencer_url, self.last_count_processed = self.group.join(self.url)
        self.sequencer = self.host.lookup_url(sequencer_url, 'Peer', 'groupcast.peer')
        self.interval_announce = interval(self.host, 3, self.proxy, 'announce_me')

    def attach_sequencer(self, sequencer_url):
        while True:
            try:
                self.sequencer = self.host.lookup_url(sequencer_url, 'Peer', 'groupcast.peer')
            except Exception:
                continue
            break

    def get_id(self):
        return self.id

    def leave_group(self):
        self.monitor.to_print("Leave: "+self.url)
        self.interval_announce.set()
        self.group.leave(self.url)

    def get_messages(self):
        return self.messages

    def get_wait_queue(self):
        return sorted(self.wait_queue.queue, key=lambda t: t[0])

    def announce_me(self):
        self.group.announce(self.url)

    def get_count(self):
        self.count += 1
        self.group.update_count(self.count)
        return self.count

    def set_count(self, count):
        self.count = count


class Sequencer(Peer):
    _tell = Peer._tell + ['multicast', 'receive', 'process_msg', 'send_multicast']

    def __init__(self):
        Peer.__init__(self)
        self.last_count_processed = -1

    def multicast(self, msg, delay = 0):
        future = self.sequencer.get_count(future = True)
        future.msg = msg
        future.delay = delay
        future.add_callback('send_multicast')

    def send_multicast(self, future):
        sleep(future.delay)
        priority = future.result()
        for peer_url in self.group.get_members():
            peer = self.host.lookup_url(peer_url, 'Peer', 'groupcast.peer')
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
        self.monitor.monitor(self.id, msg)


class Lamport(Peer):
    _tell = Peer._tell + []
    _ask = Peer._ask + []
    _ref = Peer._ref + []

    def __init__(self):
        Peer.__init__(self)
