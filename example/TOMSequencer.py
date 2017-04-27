from groupcast.Peer import *
from groupcast.Group import *
from pyactor.context import set_context, create_host, serve_forever
from groupcast.Sequencer import *

set_context()
host = create_host()

# Spawn
group = host.spawn('Group', Group)
p1 = host.spawn('Peer1', Peer)
p2 = host.spawn('Peer2', Peer)
p3 = host.spawn('Peer3', Peer)
seq = host.spawn('Seq', Sequencer)
# Attach Group
p1.attach_group(group)
p2.attach_group(group)
p3.attach_group(group)
# Attach Sequencer
p1.attach_sequencer(seq)
p2.attach_sequencer(seq)
p3.attach_sequencer(seq)
# Join Peers
group.join(p1.proxy)
group.join(p2.proxy)
group.join(p3.proxy)
# Start intervals
group.init_start()
p1.init_start()
p2.init_start()
p3.init_start()

p1.multicast("HOLA")
p2.multicast("QUE")
p3.multicast("TAL")
sleep(3)

for peer in group.get_members:
	print ("Peer" + peer.id + ": " + peer.get_queue())