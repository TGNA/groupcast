'''
Peer
Made by: Oscar Blanco and Victor Colome
'''


from Queue import PriorityQueue
from pyactor.context import interval
from pyactor.exceptions import TimeoutError


class Peer:
    _tell = ['attach_printer', 'attach_group', 'attach_sequencer', 'leave_group', 'multicast', 'receive', 'process_msg',
             'announce_me', 'set_count', 'send_multicast']
    _ask = ['get_id', 'get_messages', 'get_wait_queue', 'get_count']
    _ref = ['attach_printer', 'attach_group', 'attach_sequencer']

    def __init__(self):
        self.messages = []
        self.wait_queue = PriorityQueue()
        self.count = -1
        self.last_count_processed = -1

    def attach_printer(self, printer):
        self.printer = printer

    def attach_group(self, group):
        self.group = group
        sequencer_url, self.last_count_processed = self.group.join(self.url)
        self.sequencer = self.host.lookup_url(sequencer_url, Peer)
        self.interval_announce = interval(self.host, 3, self.proxy, 'announce_me')

    def attach_sequencer(self, sequencer_url):
        try:
            self.sequencer = self.host.lookup_url(sequencer_url, Peer)
        except Exception as e:
            self.printer.to_print(self.id+" attach_sequencer "+str(e)+" "+sequencer_url)
        # self.printer.to_print(str(self.id) + " attach seq: "+sequencer_url)

    def get_id(self):
        return self.id

    def leave_group(self):
        self.printer.to_print("Leave: "+self.url)
        self.interval_announce.set()
        self.group.leave(self.url)

    def multicast(self, msg):
        future = self.sequencer.get_count(future = True)
        future.msg = msg
        future.add_callback('send_multicast')

    def send_multicast(self, future):
        try:
            priority = future.result()
            # self.printer.to_print(str(self.id) + " seq: "+ str(self.sequencer) +"prio: "+str(priority) + "msg:"+ str(future.msg))
            for peer_url in self.group.get_members():
                peer = self.host.lookup_url(peer_url, Peer)
                peer.receive(priority, future.msg)
        except Exception as e:
            self.printer.to_print(self.id+str(e))
            # print self.id, e, " msg ", future.msg, " sequencer ", self.sequencer

    def receive(self, priority, msg):
        if(self.last_count_processed == (priority - 1)):
            self.process_msg(priority, msg)
            while not self.wait_queue.empty():
                priority, msg = self.wait_queue.get()
                if (self.last_count_processed == (priority - 1)):
                    self.process_msg(priority, msg)
                else:
                    self.wait_queue.put((priority, msg))
                    break
        else:
            self.wait_queue.put((priority, msg))

    def process_msg(self, priority, msg):
        #self.printer.to_print(self.id + " process_msg " + str(priority) + " " + msg)
        self.last_count_processed = priority
        self.messages.append(msg)

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
