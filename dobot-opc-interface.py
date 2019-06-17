import sys
sys.path.insert(0, "..")
import time
import copy

try:
    from IPython import embed
except ImportError:
    import code
    def embed():
        myvars = globals()
        myvars.update(locals())
        shell = code.InteractiveConsole(myvars)
        shell.interact()

from opcua import ua, Server, Client

import threading
import DobotDllType as dType


############### Set up Dobot API #########################

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

api = dType.load()

connectionState = None


############### Set up OPCUA server #############################

# Subscription handler
class SubHandler(object):

    def __init__(self):
        self._connectionState = connectionState

    def connection(self, connect):

        global connectionState
        
        if connect == True:
            connectionState = dType.ConnectDobot(api, "", 115200)[0]
            print("Dobot connection status:", CON_STR[connectionState])
        else: 
            dType.DisconnectDobot(api)
            connectionState = None
            print("Disconnected from Dobot")


    def datachange_notification(self, node, val, data):

        displayname = node.get_display_name().Text
        print("OPCUA: New data change event", displayname, val)

        if displayname == "Connect":
            self.connection(val)


    def event_notification(self, event):
        print("OPCUA: New event", event)


if __name__ == "__main__":

    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/dobotopcua/server/")
    server.set_server_name("Dobot FreeOpcUa Server")

    server.set_security_policy([
                ua.SecurityPolicyType.NoSecurity,
                ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
                ua.SecurityPolicyType.Basic256Sha256_Sign])

    server.load_certificate("my_cert.der")
    server.load_certificate("my_cert.pem")
    server.load_private_key("my_private_key.pem")


    # set up namespace
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)

    # import the command list node from xml
    server.import_xml("dobot-node.xml")

    # get the command node
    objects = server.get_objects_node()

    commandListNode = objects.get_child(["0:CommandList"])
    connnectCommand = commandListNode.get_child(["0:Connect"])
    homeCommand = commandListNode.get_child(["0:Home"])

    # starting server
    server.start()
    try:
        handler = SubHandler()
        sub = server.create_subscription(500, handler)
        handleHome = sub.subscribe_data_change(homeCommand)
        handleConnect = sub.subscribe_data_change(connnectCommand)

        # Test value change server side
        connectCopy = connnectCommand.get_value()
        connectCopy = copy.copy(connectCopy)
        connectCopy = True
        connnectCommand.set_value(connectCopy)

        embed()
    finally:
        server.stop()
