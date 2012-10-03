from math import cos, sin, radians
from random import randint
import json

class Player(object):
    
    def __init__(self, user, x, y):
        """
        User: the BoomProtocol instance
        """
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
            'space':self.fire,
        }
    def acceptCommands(self, actions):
        """
        actions: A list of actions the client has pushed (WASD, Fire, etc...)
        """
        for a in actions:
            self.cmd_map[a](a)


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

    def fire(self):
        return

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

