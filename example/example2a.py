from groupcast.peer import Sequencer, Lamport
from groupcast.group import Group
from groupcast.monitor import Monitor
from pyactor.context import set_context, create_host, sleep, serve_forever
T = Sequencer  # type: Sequencer | Lamport

if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:6001')
    peers = []

    monitor = host.spawn('monitor', Monitor)
    monitor.to_print("Using: "+str(T)+"\n")
    monitor.start_monitoring()

    group = host.spawn('group', Group)
    group.attach_monitor(monitor)
    group.init_start()

    serve_forever()
