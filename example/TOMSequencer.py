'''
Main TOMSequencer
Made by: Oscar Blanco and Victor Colome
'''

from groupcast.peer import Peer
from groupcast.group import Group
from groupcast.printer import Printer
from pyactor.context import set_context, create_host, sleep, serve_forever
from random import choice


N = 4
M = 10


set_context()
host = create_host()
peers = []

printer = host.spawn('printer', Printer)

group = host.spawn('Group', Group)
group.attach_printer(printer)
group.init_start()

# Peers
for i in xrange(0, N):
    p = host.spawn('Peer' + str(i), Peer)  # Spawn Peer
    p.attach_group(group)                  # Attach Group
    p.attach_printer(printer)
    peers.append(p)
    sleep(0.5)

for i in xrange(0, M):
    p = choice(peers)
    p.multicast(str(i))
    sleep(0.5)

peers[0].leave_group()
sleep(1)

# Peers
for i in xrange(N, N+N):
    p = host.spawn('Peer' + str(i), Peer)  # Spawn Peer
    p.attach_group(group)                  # Attach Group
    p.attach_printer(printer)
    peers.append(p)
    sleep(0.5)

for i in xrange(M, M+M):
    while True:
        p = choice(peers)
        if p != peers[0]:
            break
    p.multicast(str(i))
    sleep(0.5)

# for peer in peers:
#     print peer.get_id()
#     print ",".join(peer.get_messages())
#     arr_str = []
#     for p, m in peer.get_wait_queue():
#         arr_str.append("("+str(p)+","+m+")")
#     print ",".join(arr_str)
#     print "====="

sleep(1)

for peer in peers:
    print peer.get_id(), ",".join(peer.get_messages())

serve_forever()