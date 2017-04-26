'''
Peer
Made by: Oscar Blanco and Victor Colome
'''

from Queue import PriorityQueue

class Peer():
    _tell = ['attach_group', 'attach_sequencer', 'multicast', 'receive', 'process_msg', 'check_queue']
    _ask = ['']
    _ref = ['attach_group', 'attach_sequencer']

    def __init__(self):
    	self.priority_queue = PriorityQueue()
    	self.wait_queue = PriorityQueue()

    def attach_group(self, group):
    	self.group = group

    def attach_sequencer(self, sequencer):
    	self.sequencer = sequencer

    def multicast(self, msg):
    	priority = self.sequencer.get_count()
    	peers = self.group.get_members() - set([self])
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

    def check_queue(priority):
		for tupla in list(self.wait_queue.queue):
			priority = priority + 1
    		if tupla[0] == priority:
    			self.wait_queue.get()
    			self.process_msg(tupla[0], tupla[1])