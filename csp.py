import time
import copy

from panda3d.core import Vec4, VBase3
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject

(KEY_FWD,
KEY_BACK,
KEY_LEFT,
KEY_RIGHT) = range(4)

YVEC = VBase3(0, 1, 0)
XVEC = VBase3(1, 0, 0)

# Turn on this flag to view the correction.
# The server knows of a 'wall' along the x = 1
# axis that the client doesn't know about
server_only_object = 1
  
class Main(ShowBase):
    
    # The simulated one way latency between the
    # server and the client
    one_way_delay = 250 / 1000.0
    
    def __init__(self):
        ShowBase.__init__(self)
        
        self.client = Client(self)
        self.server = Server(self)
        
        t = taskMgr.add(self.update, 'update')
        t.last = 0
        
    # Updates both the client and the server
    def update(self, task):
        self.client.update()
        self.server.update()
        
        return task.cont
    
    # Sends commands from the client to the server 
    # after the simulated delay
    def sendCommands(self, cmds):
        taskMgr.doMethodLater(Main.one_way_delay, self.server.getCommands, 'sendCommands', extraArgs = [cmds])
    
    # Sends the state of the player from the server
    # to the client after the simulated delay
    def sendServerState(self, serverState, clientInputTime):
        taskMgr.doMethodLater(Main.one_way_delay, self.client.getServerState, 'sendServerState', extraArgs = [serverState, clientInputTime])
        
class State():
    
    # pos:
    # The position of the player
    
    # t:
    # The timestamp for this state
    
    def __init__(self, pos = VBase3(0, 0, 0), t = 0):
        self.pos = pos
        self.t = t
        
class InputCommands():
    
    # cmds:
    # The list of keyboard input commands
    
    # t:
    # Clients send this timestamp to the server and the server sends it back.
    
    # oldTime:
    # Used by the server. 't' is updated every tick to calculate movement,
    # so the server saves the last timestamp from the client
    # in this variable
    
    def __init__(self, cmds = [], t = 0):
        self.cmds = cmds
        self.t = t
        self.oldTime = 0
        
class Snapshot():
    
    # A snapshot consists of the state of the pawn and the
    # commands last used
    
    def __init__(self, inputCommands, state):
        self.inputCmds = inputCommands
        self.state = state
    
class SharedCode():
    
    # This function is used by both servers and clients
    # to control the movement of the 'player'. It is
    # important that they use the same function so that
    # the prediction is accurate
    @staticmethod
    def updateState(state, inputCmds):
        dt = (inputCmds.t - state.t) / 1000.0
        cmds = inputCmds.cmds
        
        moveVec = VBase3(0, 0, 0)
            
        if KEY_FWD in cmds:
            moveVec += YVEC
        elif KEY_BACK in cmds:
            moveVec -= YVEC
        if KEY_RIGHT in cmds:
            moveVec += XVEC
        elif KEY_LEFT in cmds:
            moveVec -= XVEC
            
        moveVec.normalize()
        newPos = state.pos + moveVec * 2 * dt
        
        return State(newPos, inputCmds.t + 0.0)
    
    # Returns the current time in milliseconds. 
    @staticmethod
    def getTime():
        return int(round(time.time() * 1000))
        
class Client(DirectObject):
    
    # How often the client should send
    # it's commands to the server.
    # Default set to 33Hz
    command_send_delay = 1.0 / 33
    
    def __init__(self, main):
        self.main = main
        self.delay = 0
        self.inputCommands = InputCommands()
        self.myState = State()
        self.historicalCmds = []
        self.lastTime = 0
        
        self.predictedModel = loader.loadModel('pawn')
        self.predictedModel.setColor( Vec4(0, 1, 0, 1) )
        self.predictedModel.reparentTo(render)
        
        self.serverPosModel = loader.loadModel('pawn')
        self.serverPosModel.setColor( Vec4(1, 0, 0, 1) )
        self.serverPosModel.reparentTo(render)
        
        self.setupKeyListening()
        
    # Update tick for the client.
    # During each update:
    #
    # - Update the timestamp for the commands.
    # - Send our commands to the server if enough time has passed.
    # - If so, save our commands and state to our historical list.
    # - Update our local state.
    # - Apply the state.
    def update(self):
        nowTime = SharedCode.getTime()
        self.inputCommands.t = nowTime
        self.delay += (nowTime - self.lastTime) / 1000.0
        self.lastTime = nowTime
        
        if(self.delay > Client.command_send_delay):
            self.inputCommands.cmds = self.getCommands()
            self.historicalCmds.append(copy.deepcopy((self.inputCommands, self.myState)))
            self.main.sendCommands(self.inputCommands)
            self.delay = 0
            
        # Update the state of the predicted model
        self.myState = SharedCode.updateState(self.myState, self.inputCommands)
        
        # Apply the state to the model
        self.ApplyState(self.myState)
        
    # Applies the state to the player.
    # i.e. move the player where he is supposed to be
    def ApplyState(self, myState):
        self.predictedModel.setPos(myState.pos)
        
    # Called when the server state is received by the
    # client
    def getServerState(self, serverState, clientInputTime):
        self.serverPosModel.setPos(serverState.pos)
        self.verifyPrediction(serverState, clientInputTime)
        
    # Here, we compare our historical location
    # to where the server says we are. If somehow we are off
    # by a lot, we recalculate our position by looping
    # through the commands we saved
    def verifyPrediction(self, serverState, clientInputTime):
        
        # Remove old commands
        while len(self.historicalCmds) > 0 and self.historicalCmds[0][0].t < clientInputTime:
            self.historicalCmds.pop(0)
        
        if self.historicalCmds:
            diff =  (serverState.pos - self.historicalCmds[0][1].pos).length()
            print diff
            
            # Recalculate position
            if(diff > 0.2):
                for oldState in self.historicalCmds:
                    serverState = SharedCode.updateState(serverState, oldState[0])
                
                self.ApplyState(serverState)
                self.myState.pos = serverState.pos
            
    # Returns a list of the commands being issued
    # by the player. i.e. the keys being pressed
    def getCommands(self):
        keys = []
        
        if (self.keyMap['KEY_FWD']):
            keys.append(KEY_FWD)
            
        elif (self.keyMap['KEY_BACK']):
            keys.append(KEY_BACK)
            
        if (self.keyMap['KEY_RIGHT']):
            keys.append(KEY_RIGHT)
            
        elif (self.keyMap['KEY_LEFT']):
            keys.append(KEY_LEFT)

        return keys
    
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    def setupKeyListening(self):
        self.keyMap = {"KEY_FWD":0, "KEY_BACK":0, "KEY_LEFT":0, "KEY_RIGHT":0}
         
        self.accept("w", self.setKey, ['KEY_FWD', 1])
        self.accept("s", self.setKey, ['KEY_BACK', 1])
        self.accept("a", self.setKey, ['KEY_LEFT', 1])
        self.accept("d", self.setKey, ['KEY_RIGHT', 1])
        
        self.accept("w-up", self.setKey, ['KEY_FWD', 0])
        self.accept("s-up", self.setKey, ['KEY_BACK', 0])
        self.accept("a-up", self.setKey, ['KEY_LEFT', 0])
        self.accept("d-up", self.setKey, ['KEY_RIGHT', 0])
    
    
class Server():
    
    # How often the client should send
    # it's commands to the server.
    # Default set to 20Hz
    position_send_delay = 1.0 / 20
    
    def __init__(self, main):
        self.main = main
        self.delay = 0
        self.playerState = State()
        self.inputCommands = InputCommands()
        self.inputCommands.oldTime = float('+infinity')
        self.gotCmds = False
        self.lastTime = 0
    
    # Update tick for the server.
    # During each update:
    #
    # - Update the timestamp for the commands.
    # - Send the state of the player if enough time has passed.
    # - Update the local state.
    def update(self):
        nowTime = SharedCode.getTime()
        self.inputCommands.t = nowTime
        self.delay += (nowTime - self.lastTime) / 1000.0
        self.lastTime = nowTime
        
        if(self.delay > Server.position_send_delay):
            if(self.gotCmds):
                self.main.sendServerState(self.playerState, self.inputCommands.oldTime)
            self.delay = 0
                
        self.playerState = SharedCode.updateState(self.playerState, self.inputCommands)
        
        # If the server knows about the wall that the
        # client doesn't
        if server_only_object:
            if self.playerState.pos.getX() > 1:
                self.playerState.pos.setX(1)
      
    # Called when the client commands are received by the server
    def getCommands(self, cmds):
        self.gotCmds = True
        self.inputCommands = cmds
        self.inputCommands.oldTime = copy.deepcopy(cmds.t)
 
app = Main() 
app.run()