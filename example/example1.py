from groupcast.peer import *
from groupcast.group import Group
from groupcast.monitor import Monitor
from pyactor.context import set_context, create_host, serve_forever
from util import *
from random import uniform


N = 4  # n. peers, it creates the double
M = 10  # n. messages, it creates the double
T = Lamport  # type: Sequencer | Lamport


if __name__ == "__main__":
    set_context('green_thread')
    host = create_host()
    peers = {}

    monitor = host.spawn('monitor', Monitor)
    monitor.to_print("Using: " + T.__name__ + "\n")
    monitor.start_monitoring()

    group = host.spawn('group', Group)
    group.attach_monitor(monitor)
    group.init_start()

    create_peers(0, N, peers, group, monitor, T, host)

    create_messages(0, M, peers, uniform(0.1, 0.6))

    sleep(1)
    peer_leave_group(peers, 'peer00')
    sleep(3)

    create_peers(N, N+N, peers, group, monitor, T, host)

    create_messages(M, M+M, peers, uniform(0.1, 0.6))

    serve_forever()
