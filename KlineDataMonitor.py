from KlineDataObserver import KlineDataObserver



class KlineDataMonitor(KlineDataObserver):
    def __init__(self, name=''):
        KlineDataObserver.__init__(self)
        self.name = name
        self._data = 0

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.notify()