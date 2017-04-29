'''
Main TOMSequencer
Made by: Oscar Blanco and Victor Colome
'''

from groupcast.peer import *
from groupcast.group import *
from groupcast.printer import *
from pyactor.context import set_context, create_host, sleep
from random import choice

set_context()
host = create_host()

N = 3                                       # Number of Peers
peers = []

printer = host.spawn('printer', Printer)

# Group
group = host.spawn('Group', Group)
group.attach_printer(printer)
group.init_start()

# Peers
for i in range(N):
    p = host.spawn('Peer' + str(i), Peer) # Spawn Peer
    p.attach_group(group)            # Attach Group
    p.attach_printer(printer)
    peers.append(p)

for i in range(10):
    choice(peers).multicast("Message " + str(i))

sleep(3)

for peer in peers:
    print (peer.get_id() + ": " + ",".join(peer.get_queue()))