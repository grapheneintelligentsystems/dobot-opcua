import sys
sys.path.insert(0, "..")

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()


from opcua import Client
import DobotDllType as dType
import threading

############### Set up Dobot API #########################

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

api = dType.load()

connectionState = None


############### Set up OPCUA server #############################

class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """
    def __init__(self):
        
        global connectionState
        self._connectionState = connectionState
        self.J1pos = 0
        self.J2pos = 0
        self.J3pos = 0

    def connection(self, connect):

        global connectionState
        
        if connect == True:
            connectionState = dType.ConnectDobot(api, "", 115200)[0]
            print("Dobot connection status:", CON_STR[connectionState])
            # set up
            self.getCurrentPos()
            self.setupJOGparams()
            # create separate thread for PTP motions
            PTPthread = threading.Thread(target=self.PTProutine)
            PTPthread.start()
        else: 
            dType.DisconnectDobot(api)
            connectionState = None
            print("Disconnected from Dobot")
    
    def PTProutine(self):
        global connectionState

        while(connectionState == dType.DobotConnect.DobotConnect_NoError):
            dType.SetPTPCmd(api, 4, self.J1pos, self.J2pos, self.J3pos, self.rHead, isQueued = 0)
            dType.dSleep(500)

    def getCurrentPos(self):
        pos = dType.GetPose(api)
        self.J1pos = pos[4]
        self.J2pos = pos[5]
        self.J3pos = pos[6]
        self.rHead = pos[3]

    def setupJOGparams(self):
        global connectionState

        if (connectionState == dType.DobotConnect.DobotConnect_NoError): 
            #Clean Command Queued
            dType.SetQueuedCmdClear(api)

            #Async JOG Params Setting
            dType.SetHOMEParams(api, 250, 0, 50, 0, isQueued = 1)
            dType.SetPTPJointParams(api,200,200,200,200,200,200,200,200, isQueued = 1)
            dType.SetPTPCommonParams(api, 100, 100, isQueued = 1)

            #Async Home
            #dType.SetHOMECmd(api, temp = 0, isQueued = 1)
            
        else:
            print(connectionState)

    def jogJ1(self, newJ1pos):
        self.J1pos = newJ1pos

    def jogJ2(self, newJ2pos):
        self.J2pos = 85-(newJ2pos - 55) # offset from Visual Components and real angle
        print(self.J2pos)        

    def jogJ3(self, newJ3pos):
        self.J3pos = 95-(newJ3pos + 45) # offset from Visual Components and real angle
        print(self.J3pos)         

    def datachange_notification(self, node, val, data):

        displayname = node.nodeid.Identifier.replace("MAIN.","")
        print("OPCUA: New data change event", displayname, val)

        if displayname == "Connect":
            self.connection(val)
        if displayname == "J1":
            self.jogJ1(val)
        if displayname == "J2":
            self.jogJ2(val)
        if displayname == "J3":
            self.jogJ3(val)


    def event_notification(self, event):
        print("OPCUA: New event", event)


if __name__ == "__main__":

    client = Client("opc.tcp://192.168.111.1:4840/admin")
    # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Objects node is: ", root)

        # Now getting a variable node using its browse path
        obj = root.get_child(["0:Objects"])
        print("MyObject is: ", obj)

        plcNode = obj.get_child(["4:PLC1"])
        mainNode = plcNode.get_child(["4:MAIN"])
        #testIntVar = mainNode.get_child(["4:x"])

        Connect = mainNode.get_child(["4:Connect"])

        J1 = mainNode.get_child(["4:J1"])
        J2 = mainNode.get_child(["4:J2"])
        J3 = mainNode.get_child(["4:J3"])

        handler = SubHandler()
        sub = client.create_subscription(10, handler)

        #handleTestVar = sub.subscribe_data_change(testIntVar)
        handleJ1 = sub.subscribe_data_change(J1)
        handleJ2 = sub.subscribe_data_change(J2)
        handleJ3 = sub.subscribe_data_change(J3)
        handleConnect = sub.subscribe_data_change(Connect)    

        # handle = sub.subscribe_events(obj, myevent)
        # handleHome = sub.subscribe_data_change(homeCommand)
        # handleConnect = sub.subscribe_data_change(connectCommand)

        embed()
        # sub.unsubscribe(handleHome)
        # sub.unsubscribe(handleConnect)
        sub.delete()
    finally:
        client.disconnect()