import sys
sys.path.insert(0, "..")
import time
from collections import OrderedDict

from opcua import ua, Server, instantiate
from opcua.common.xmlexporter import XmlExporter

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()



# method to be exposed through server

def func(parent, variant):
    ret = False
    if variant.Value % 2 == 0:
        ret = True
    return [ua.Variant(ret, ua.VariantType.Boolean)]





if __name__ == "__main__":

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/xml-server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()

    # populating our address space
    myobj = objects.add_object(idx, "MyObject")

    mymethod = myobj.add_method(idx, "mymethod", func, [ua.VariantType.Int64], [ua.VariantType.Boolean])

    # starting!
    server.start()

    # exporter = XmlExporter(server)
    # exporter.build_etree(node_list, ['http://myua.org/test/'])
    # exporter.write_xml('ua-export.xml')

    try:
        embed()
    finally:
        server.stop()

server.stop()