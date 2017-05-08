from groupcast.peer import Sequencer, Lamport
from groupcast.group import Group
from groupcast.printer import Printer
from pyactor.context import set_context, create_host, sleep, shutdown
from random import choice


N = 4  # n. peers, it creates the double
M = 10  # n. messages, it creates the double
T = Sequencer  # type: Sequencer | Lamport


def create_peers(s, e):
    for i in xrange(s, e):
        p = host.spawn('Peer' + str(i), T)
        p.attach(printer, group)
        peers.append(p)
        sleep(0.5)


def create_messages(s, e, leave = []):
    aux = list(set(peers) - set(leave))
    for i in xrange(s, e):
        p = choice(aux)
        p.multicast(str(i))
        sleep(0.5)


def print_table(queue=False):
    if queue:
        for peer in peers:
            print peer.get_id()
            print ",".join(peer.get_messages())
            arr_str = []
            for p, m in peer.get_wait_queue():
                arr_str.append("("+str(p)+","+m+")")
            print ",".join(arr_str)
            print "====="

    for peer in peers:
        print peer.get_id(), ",".join(peer.get_messages())


if __name__ == "__main__":
    print "Using: "+str(T)

    set_context()
    host = create_host()
    peers = []
    leave = []

    printer = host.spawn('printer', Printer)

    group = host.spawn('Group', Group)
    group.attach_printer(printer)
    group.init_start()

    create_peers(0, N)

    create_messages(0, M)

    leave.append(peers[0])
    peers[0].leave_group()
    sleep(1)

    create_peers(N, N+N)

    create_messages(M, M+M, leave)

    sleep(2)

    print_table()

    shutdown()
