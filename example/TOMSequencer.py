'''
Main TOMSequencer
Made by: Oscar Blanco and Victor Colome
'''

from groupcast.Peer import *
from groupcast.Group import *
from pyactor.context import set_context, create_host, serve_forever
from groupcast.Sequencer import *

set_context()
host = create_host()

N = 3                                       # Number of Peers
peers = []
# Group
group = host.spawn('Group', Group)
group.init_start()
# Sequencer
seq = host.spawn('Peer' + N, Peer)
seq.attach_group(group)
group.join(seq.proxy)
seq.init_start()
# Peers
for i in range(N):
    peers[i] = host.spawn('Peer' + i, Peer) # Spawn Peer
    peers[i].attach_group(group)            # Attach Group
    peers[i].attach_sequencer(seq)          # Attach Sequencer
    group.join(peers[i].proxy)              # Join to Group
    peers[i].init_start()                   # Start interval

for i in range(N):
    peers[i].multicast("Message " + i)

sleep(3)

for peer in group.get_members():
    print (peer.id + ": " + peer.get_queue())