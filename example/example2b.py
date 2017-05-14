from groupcast.peer import *
from pyactor.context import set_context, create_host, serve_forever
from util import *


N = 4  # n. peers, it creates the double
M = 10  # n. messages, it creates the double
T = Sequencer  # type: Sequencer | Lamport


if __name__ == "__main__":
    set_context('green_thread')
    host = create_host('http://127.0.0.1:6002')
    peers = {}

    monitor = host.lookup_url('http://127.0.0.1:6001/monitor', 'Monitor', 'groupcast.monitor')
    group = host.lookup_url('http://127.0.0.1:6001/group', 'Group', 'groupcast.group')

    create_peers(0, N, peers, group, monitor, T, host)

    create_messages(0, M, peers)

    serve_forever()
