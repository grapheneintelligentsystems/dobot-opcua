import sys
sys.path.insert(0, "..")
import time

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


############### Set up OPCUA server #############################

# Subscription handler
class SubHandler(object):

    def datachange_notification(self, node, val, data):
        print("OPCUA: New data change event", node, val)

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

    # set up namespace
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)

    # import the command list node from xml
    server.import_xml("dobot-node.xml")

    # create the default event object
    myevgen = server.get_event_generator()
    myevgen.event.Severity = 300

    # starting server
    server.start()
    try:
        embed()
    finally:
        server.stop()


############### Set up OPCUA command list #############################

# commandList = server.nodes.objects.add_object(idx, "CommandList")

# connectDobot = commandList.add_variable(idx, "ConnectDobot", True, ua.VariantType.Boolean)
# connectDobot.set_writable()  

# home = commandList.add_variable(idx, "Home", False, ua.VariantType.Boolean)
# home.set_writable()   
    

############### Start the dobot client #############################

# if __name__ == "__main__":

#     client = Client("opc.tcp://localhost:4840/freeopcua/server/")
    
#     try:
#         client.connect()

#         root = client.get_root_node()
#         print("Objects node is: ", root)
#         print("Children of root are: ", root.get_children())

#         # Getting a variable node using its browse path
#         homeCommand = root.get_child(["0:Objects", "2:CommandList", "2:Home"])
#         connectDobotCommand = root.get_child(["0:Objects", "2:CommandList", "2:ConnectDobot"])
#         print("home is: ", homeCommand.get_value())
#         print("connect is: ", connectDobotCommand.get_value())
        
#         while True:
            
#             if connectDobotCommand.get_value() == True:

#                 #Connect Dobot
#                 state = dType.ConnectDobot(api, "", 115200)[0]
#                 print("Connect status:",CON_STR[state])

#                 if (state == dType.DobotConnect.DobotConnect_NoError): 
                    
#                     #Clean Command Queued
#                     dType.SetQueuedCmdClear(api) 
                    
#                     #Async Motion Params Setting
#                     dType.SetHOMEParams(api, 250, 0, 50, 0, isQueued = 1)
#                     dType.SetHOMECmd(api, temp = 0, isQueued = 1)

#                     #Start to Execute Command Queued
#                     dType.SetQueuedCmdStartExec(api)
#                     dType.SetQueuedCmdStopExec(api)

#             else:
                    
#                 #Disconnect Dobot
#                 dType.DisconnectDobot(api)

#     finally:
#         client.disconnect()


    