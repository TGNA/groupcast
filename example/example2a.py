from groupcast.group import Group
from groupcast.monitor import Monitor
from pyactor.context import set_context, create_host, serve_forever

if __name__ == "__main__":
    set_context()
    host = create_host('http://127.0.0.1:6001')
    peers = []

    monitor = host.spawn('monitor', Monitor)
    monitor.start_monitoring()

    group = host.spawn('group', Group)
    group.attach_monitor(monitor)
    group.init_start()

    serve_forever()
