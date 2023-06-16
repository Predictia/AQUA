import sys
from aqua import Reader
sys.path.insert(0, '../')
from seaice_class import SeaIceExtent


# temporary hack if your env-dummy.yml
# does not install your diagnostic.
sys.path.insert(0, '../')

# Empty class to be filled with your diagnostic
# It prints the catalogue as example of what you can do
# with the aqua module

object = SeaIceExtent()
object.run()
