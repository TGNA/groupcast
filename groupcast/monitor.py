from pyactor.context import interval


class Monitor(object):
    _tell = ['to_print', 'start_monitoring', 'stop_monitoring', 'monitor',
             'print_table']

    def __init__(self):
        self.peers = {}
        self.printed = False

    def to_print(self, string):
        print string

    def start_monitoring(self):
        self.interval_monitoring = interval(self.host, 1, self.proxy,
                                            'print_table')

    def stop_monitoring(self):
        self.interval_monitoring.set()

    def monitor(self, peer, msg):
        try:
            self.peers[peer].append(msg)
        except KeyError:
            self.peers[peer] = [msg]
        self.printed = True

    def print_table(self):
        if self.printed:
            printer = ""

            peers = sorted(self.peers.items(), key=lambda t: t[0])
            for peer, data in peers:
                printer += (peer+": "+",".join(data)+"\n")

            self.to_print(printer)
            self.printed = False
