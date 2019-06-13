import sys
sys.path.insert(0, "..")
import time

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

if __name__ == "__main__":

    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)

    # starting server
    server.start()


############### Set up OPCUA command list #############################

commandList = server.nodes.objects.add_object(idx, "CommandList")

connectDobot = commandList.add_variable(idx, "ConnectDobot", True, ua.VariantType.Boolean)
connectDobot.set_writable()  

home = commandList.add_variable(idx, "Home", False, ua.VariantType.Boolean)
home.set_writable()   
    

############### Start the dobot client #############################

if __name__ == "__main__":

    client = Client("opc.tcp://localhost:4840/freeopcua/server/")
    
    try:
        client.connect()

        root = client.get_root_node()
        print("Objects node is: ", root)
        print("Children of root are: ", root.get_children())

        # Getting a variable node using its browse path
        homeCommand = root.get_child(["0:Objects", "2:CommandList", "2:Home"])
        connectDobotCommand = root.get_child(["0:Objects", "2:CommandList", "2:ConnectDobot"])
        print("home is: ", homeCommand.get_value())
        print("connect is: ", connectDobotCommand.get_value())
        
        while True:
            
            if connectDobotCommand.get_value() == True:

                #Connect Dobot
                state = dType.ConnectDobot(api, "", 115200)[0]
                print("Connect status:",CON_STR[state])

                if (state == dType.DobotConnect.DobotConnect_NoError): 
                    
                    #Clean Command Queued
                    dType.SetQueuedCmdClear(api) 
                    
                    #Async Motion Params Setting
                    dType.SetHOMEParams(api, 250, 0, 50, 0, isQueued = 1)
                    dType.SetHOMECmd(api, temp = 0, isQueued = 1)

                    #Start to Execute Command Queued
                    dType.SetQueuedCmdStartExec(api)
                    dType.SetQueuedCmdStopExec(api)

            else:
                    
                #Disconnect Dobot
                dType.DisconnectDobot(api)

    finally:
        client.disconnect()


    