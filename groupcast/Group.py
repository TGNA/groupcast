'''
Group
Made by: Oscar Blanco and Victor Colome
'''

class Group():
    _tell = ['join', 'leave']
    _ask = ['get_members']
    _ref = ['join', 'leave', 'get_members']

  	def __init__(self):
  		self.peers = set()

  	def join(self, peer):
  		self.peers.add(peer)

  	def leave(self, peer):
  		self.peers.discard(peer)	# remove da KeyError

  	def get_members(self):
  		return list(self.peers)