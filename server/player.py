from math import cos, sin, radians
from random import randint
import json

from twisted.internet import reactor

from bullet import Bullet
import time
import copy

class InputCommands():
    """
    cmds - The list of keyboard input commands

    # t:
    # Clients send this timestamp to the server and the server sends it back.
    """

    def __init__(self, cmds=[], t=0):
        self.cmds = cmds
        self.t = t


class Player(object):
    
    def __init__(self, world, user, x, y):
        """
        User: the BoomProtocol instance
        """
        #last time stamp recieved from this client
        self.last_ts = 0

        #input commands that haven't been processed
        self.input_commands = InputCommands()
        #processed commands
        self.processed_commands = []

        self.pid = randint(1,500)
        self.boom = user
        
        #Friction Factor
        self.ff = .5
        self.velocity = [0, 0]

        #rotation
        self.rot = 0        

        #base
        self.x = x
        self.y = y

        #turret
        self.trot = 0
        self.tx = x
        self.ty = y

        self.cmd_map = {
            'w':self.move,
            's':self.move,
            'a':self.rotate,
            'd':self.rotate,
            'left':self.rotateTurret,
            'right':self.rotateTurret,
            'fire':self.fire,
        }

        #bullets
        self.loading = False 
        self.new_bullets = []
        self.bullet_list = []

        #The world this player belongs to
        self.world = world
        self.world.add(self)

    def processData(self, data):
        if 'actions' in data:
            self.acceptCommands(data['actions'], data['cts'])

            self.last_ts = data['cts']

    def acceptCommands(self, actions, t):
        """
        actions: groups of actions the client has pushed (WASD, Fire, etc...)
        """
        self.input_commands.t = t
        for action_group in actions:
            #print action_group['calc_timestamp']
            self.input_commands.cmds.append(action_group['list'])

    def update(self):
        """
        Called every 100 milliseconds I think
        """
        for action_group in self.input_commands.cmds:
            for cmd in action_group:
                self.cmd_map[cmd](cmd)
        self.processed_commands.append(copy.deepcopy(self.input_commands))
        self.input_commands.cmds = []

        if len(self.processed_commands) < 100:
            self.processed_commands.pop(0)
        #print self.toObj()

    def move(self, direction):
        a = [0.0,0.0]

        a[0] += cos(radians(self.rot+90))*.9
        a[1] += sin(radians(self.rot+90))*.9

        ff = .5 # Friction Factor

        self.velocity[0] *= self.ff
        self.velocity[1] *= self.ff

        self.velocity[0] += a[0]
        self.velocity[1] += a[1]

        if direction == 'w':
            self.x -= self.velocity[0]
            self.y -= self.velocity[1]
            self.tx = self.x
            self.ty = self.y 
        
        else:
            self.x += self.velocity[0]
            self.y += self.velocity[1]
            self.tx = self.x
            self.ty = self.y


    def rotate(self, direction):
        if direction == 'a':
            self.rot -= 1
        else:
            self.rot += 1

    def rotateTurret(self, direction):
        if direction == 'left':
            self.trot -= 1
        else:
            self.trot += 1

    def fire(self, useless):
        
        if not self.loading:
            self.loading = True
            angle_radians = radians(self.trot)

            bullet_x = self.tx + sin(angle_radians)
            bullet_y = self.ty + cos(angle_radians)
            print 'new bullet'
            bullet = Bullet(self.world, self, self.x, self.y, self.trot)
            
            #time it takes to reload
            reactor.callLater(1, self.doneReloading)

    def doneReloading(self):
        self.loading = False

    def toJSON(self):
        return json.dumps({
            'pid':self.pid,
            'x':self.x,
            'y':self.y,
            'rot':self.rot,
            'tx':self.tx,
            'ty':self.ty,
            'trot':self.trot
        })

    def toObj(self):
        return {
            'pid':self.pid,
            'x':self.x,
            'y':self.y,
            'rot':self.rot,
            'tx':self.tx,
            'ty':self.ty,
            'trot':self.trot
        }

