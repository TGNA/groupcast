from Queue import PriorityQueue
from pyactor.context import interval, sleep
from groupcast.dict_queue import DictQueue
from random import choice
from pyactor.exceptions import NotFoundError
from threading import Lock


class Peer(object):
    _tell = ['attach', 'attach_monitor', 'attach_group', 'leave_group',
             'announce_me', 'multicast', 'receive']
    _ask = ['get_id', 'get_messages', 'get_wait_queue']
    _ref = ['attach', 'attach_monitor', 'attach_group']

    def __init__(self):
        self.messages = []
        self.count = -1
        self.lookups = {}

    def attach(self, monitor, group):
        self.attach_monitor(monitor)
        self.attach_group(group)

    def attach_monitor(self, monitor):
        self.monitor = monitor

    def attach_group(self, group):
        self.group = group
        self.interval_announce = interval(self.host, 2, self.proxy,
                                          'announce_me')

    def get_id(self):
        return self.id

    def leave_group(self):
        self.interval_announce.set()
        self.group.leave(self.url)
        self.host.stop_actor(self.id)

    def get_messages(self):
        return self.messages

    def announce_me(self):
        self.group.announce(self.url)

    def lookup(self, url, klass, module='groupcast.peer'):
        try:
            if url == self.url:
                return self.proxy
            else:
                return self.lookups[url]
        except KeyError:
            try:
                future = self.host.lookup_url(url, klass, module, future=True)
                self.lookups[url] = future.result()
                return self.lookups[url]
            except Exception:
                raise NotFoundError

    def get_wait_queue(self):
        raise NotImplementedError

    def multicast(self):
        raise NotImplementedError

    def receive(self):
        raise NotImplementedError


class Sequencer(Peer):
    _tell = Peer._tell + ['send_multicast', 'start_elections', 'set_count',
                          'attach_sequencer']
    _ask = Peer._ask + ['get_sequencer_url', 'get_count', 'vote']
    _ref = Peer._ref + ['send_multicast', 'get_sequencer_url']

    def __init__(self):
        Peer.__init__(self)
        self.wait_queue = PriorityQueue()
        self.last_count_processed = -1
        self.in_elections = Lock()

    def attach_group(self, group):
        super(Sequencer, self).attach_group(group)
        members = list(set(self.group.get_members()) - set(self.url))
        try:
            member = self.lookup(choice(members), 'Sequencer')
            seq_url, elections = member.get_sequencer_url()
            self.attach_sequencer(seq_url)
            if elections:
                self.in_elections.acquire()
        except IndexError:
            self.sequencer_url = self.url
            self.sequencer = self.proxy
        except NotFoundError:
            self.start_elections()

    def attach_sequencer(self, sequencer_url, count=(-1)):
        self.sequencer_url = sequencer_url
        self.sequencer = self.lookup(sequencer_url, 'Sequencer')
        try:
            self.in_elections.release()
        except Exception:
            pass
        self.last_count_processed = count

    def get_sequencer_url(self):
        return (self.sequencer_url, self.in_elections.locked())

    def multicast(self, msg, delay=0):
        future = self.sequencer.get_count(future=True)
        future.msg = msg
        future.delay = delay
        future.add_callback('send_multicast')

    def send_multicast(self, future):
        priority = future.result()
        sleep(future.delay)
        for peer_url in self.group.get_members():
            peer = self.lookup(peer_url, 'Sequencer')
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
        try:
            self.monitor.monitor(self.id, msg)
        except AttributeError:
            pass

    def get_wait_queue(self):
        return sorted(self.wait_queue.queue, key=lambda t: t[0])

    def get_count(self):
        self.count += 1
        return self.count

    def set_count(self, count):
        self.count = count

    def start_elections(self):
        if not self.in_elections.locked():
            self.in_elections.acquire()
            try:
                self.monitor.to_print("Starting elections from "+self.id)
            except AttributeError:
                pass
            votes = set([self.url])
            members = self.group.get_members()

            for peer_url in members:
                peer = self.lookup(peer_url, 'Sequencer')
                votes.add(peer.vote())
                try:
                    self.monitor.to_print("Vote: "+peer_url)
                except AttributeError:
                    pass
            new_coordinator_url = max(votes)

            try:
                self.monitor.to_print("New sequencer:"+new_coordinator_url+"\n")
            except AttributeError:
                pass

            if new_coordinator_url == self.url:
                last_count = self.get_count()
            else:
                new_coordinator = self.lookup(new_coordinator_url, 'Sequencer')
                last_count = new_coordinator.get_count()

            self.attach_sequencer(new_coordinator_url, last_count)
            members = self.group.get_members()
            for peer_url in members:
                peer = self.lookup(peer_url, 'Sequencer')
                peer.attach_sequencer(new_coordinator_url, last_count)

    def vote(self):
        self.in_elections.acquire()
        return self.url


class Lamport(Peer):

    def __init__(self):
        Peer.__init__(self)
        self.wait_queue = DictQueue()
        self.acks = {}

    def increment_count(self):
        self.count += 1
        return self.count

    def multicast(self, msg, delay=0):
        sleep(delay)
        priority = self.increment_count()
        members = self.group.get_members()
        n_acks = len(members)
        for peer_url in members:
            peer = self.lookup(peer_url, 'Lamport')
            peer.receive(priority, msg, n_acks)

    def receive(self, priority, msg, size=None):
        if size is not None:
            try:
                self.acks[msg] += size
                new_priority = max(self.wait_queue[msg], priority) + 1
                self.wait_queue[msg] = new_priority
                self.count = new_priority
            except KeyError:
                self.acks[msg] = size
                self.wait_queue[msg] = priority
                self.count = max(priority, self.count)

            priority = self.increment_count()
            for peer_url in self.group.get_members():
                peer = self.lookup(peer_url, 'Lamport')
                peer.receive(priority, msg)
        else:
            try:
                self.acks[msg] -= 1
                new_priority = max(self.wait_queue[msg], priority) + 1
                self.wait_queue[msg] = new_priority
                self.count = new_priority
            except KeyError:
                self.acks[msg] = -1
                self.wait_queue[msg] = priority
                self.count = priority

            while not self.wait_queue.empty():
                priority, msg = self.wait_queue.pop_smallest()
                if self.acks[msg] == 0:
                    self.process_msg(msg)
                    del self.acks[msg]
                else:
                    self.wait_queue[msg] = priority
                    break

    def process_msg(self, msg):
        self.messages.append(msg)
        try:
            self.monitor.monitor(self.id, msg)
        except AttributeError:
            pass

    def get_wait_queue(self):
        return self.wait_queue.queue()
