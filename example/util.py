from pyactor.context import sleep
from random import choice


def create_peers(s, e, peers, group, monitor, t, host):
    for i in xrange(s, e):
        peer_id = 'peer' + str(i).zfill(2)
        p = host.spawn(peer_id, t)
        p.attach(monitor, group)
        peers[peer_id] = p
        sleep(0.5)


def create_messages(s, e, peers, delay=0):
    for i in xrange(s, e):
        p = choice(peers.values())
        p.multicast(str(i), delay)
        sleep(0.5)


def peer_leave_group(peers, peer_id):
    peers[peer_id].leave_group()
    del peers[peer_id]


def print_table(peers):
    for peer in peers.values():
        print peer.get_id()
        print "Processed: "+",".join(peer.get_messages())
        arr_str = []
        for p, m in peer.get_wait_queue():
            arr_str.append("("+str(p)+","+str(m)+")")
        print "Queue: "+",".join(arr_str)
        print "====="