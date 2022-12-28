from KlineDataObserver import KlineDataObserver



class KlineDataMonitor(KlineDataObserver):
    def __init__(self, tf, pair, name=''):
        KlineDataObserver.__init__(self)
        self.name = name
        self.tf = tf
        self.pair = pair
        self._data = 0

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.notify()

    def get_tf(self):
        return self.tf

    def get_pair(self):
        return self.pair