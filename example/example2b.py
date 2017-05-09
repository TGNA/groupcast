from groupcast.peer import Sequencer, Lamport
from groupcast.monitor import Monitor
from pyactor.context import set_context, create_host, sleep, serve_forever, interval
from random import choice, uniform


N = 4  # n. peers, it creates the double
M = 10  # n. messages, it creates the double
T = Sequencer  # type: Sequencer | Lamport

def create_peers(s, e):
    for i in xrange(s, e):
        p = host.spawn('peer' + str(i), T)
        p.attach(monitor, group)
        peers.append(p)
        sleep(0.5)


def create_messages(s, e, leave = []):
    aux = list(set(peers) - set(leave))
    for i in xrange(s, e):
        p = choice(aux)
        delay = uniform(0.1, 0.9)
        p.multicast(str(i), delay)
        sleep(0.5)


if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:6002')
    peers = []
    leave = []

    monitor = host.lookup_url('http://127.0.0.1:6001/monitor', 'Monitor', 'groupcast.monitor')
    group = host.lookup_url('http://127.0.0.1:6001/group', 'Group', 'groupcast.group')

    create_peers(0, N)

    create_messages(0, M)

    sleep(1)
    leave.append(peers[0])
    peers[0].leave_group()
    sleep(1)

    create_peers(N, N + N)

    create_messages(M, M + M, leave)

    serve_forever()
