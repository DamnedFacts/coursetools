from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

with open('config.yaml') as f:
    config = load(f, Loader=Loader)
