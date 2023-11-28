from aqua.util import ConfigPath

if __name__ == "__main__":
    configdir=None
    Configurer = ConfigPath(configdir=configdir)
    print(Configurer.machine)