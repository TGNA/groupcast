'''
Main TOMSequencer
Made by: Oscar Blanco and Victor Colome
'''

from groupcast.peer import *
from groupcast.group import *
from groupcast.printer import *
from pyactor.context import set_context, create_host, sleep, serve_forever
from random import choice

set_context()
host = create_host()
peers = []

printer = host.spawn('printer', Printer)

group = host.spawn('Group', Group)
group.attach_printer(printer)
group.init_start()

# Peers
for i in xrange(3):
    p = host.spawn('Peer' + str(i), Peer)  # Spawn Peer
    p.attach_group(group)                  # Attach Group
    p.attach_printer(printer)
    peers.append(p)

for i in xrange(10):
    p = choice(peers)
    p.multicast(str(i))
    sleep(0.5)

print "Peer0 Leave"
peers[0].leave_group()
sleep(2)

p = host.spawn('Peer3', Peer)  # Spawn Peer
p.attach_group(group)          # Attach Group
p.attach_printer(printer)
peers.append(p)

p = host.spawn('Peer4', Peer)  # Spawn Peer
p.attach_group(group)          # Attach Group
p.attach_printer(printer)
peers.append(p)

p = host.spawn('Peer5', Peer)  # Spawn Peer
p.attach_group(group)          # Attach Group
p.attach_printer(printer)
peers.append(p)

p = host.spawn('Peer6', Peer)  # Spawn Peer
p.attach_group(group)          # Attach Group
p.attach_printer(printer)
peers.append(p)

sleep(1)

for i in xrange(10, 20):
    p = choice(peers)
    p.multicast(str(i))
    sleep(0.5)

sleep(3)

# for peer in peers:
#     print peer.get_id()
#     print ",".join(peer.get_messages())
#     arr_str = []
#     for p, m in peer.get_wait_queue():
#         arr_str.append("("+str(p)+","+m+")")
#     print ",".join(arr_str)
#     print "====="

for peer in peers:
    print peer.get_id(), ",".join(peer.get_messages())

serve_forever()