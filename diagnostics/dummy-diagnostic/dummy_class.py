from aqua import catalogue


class DummyDiagnostic():
    def __init__(self, option=None, configdir=None):
        self.option = option
        self.configdir = configdir

    def run(self):
        cat = catalogue(configdir=self.configdir)
        print(cat)
