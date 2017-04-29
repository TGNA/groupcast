'''
Sequencer
Made by: Oscar Blanco and Victor Colome
'''


class Sequencer():
    _tell = ['set_counter']
    _ask = ['get_counter', 'is_sequencer']
    _ref = []

    def __init__(self):
        self.count = 0

    def get_counter(self):
        self.count = self.count + 1
        return self.count

    def set_counter(self, count):
        self.count = count

    def is_sequencer(self):
        return self.id == self.sequencer.id
