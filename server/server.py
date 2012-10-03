from txsockjs.factory import SockJSFactory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Factory, ClientFactory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, protocol

from player import Player

import time
import json
from random import randint


class BoomProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        print 'connection made'
        self.factory.addUser(self)
        #self.sendLine(json.dumps({'test':'message'}))

    def dataReceived(self, data):
        self.factory.processData(data)

    def connectionLost(self, something):
        print 'connection lost'
        self.factory.users.remove(self)
        

class GameFactory(Factory):

    def __init__(self):
        self.users = set()

    def addUser(self, user):
        
        #random location
        rx = randint(10,500)
        ry = randint(10,500)
        p = Player(user, 300, 300)
        
        #send all the current players first
        p.boom.sendLine(json.dumps({"player_list":self.playerList()}))
        self.users.add(p)

        for u in self.users:
            u.boom.sendLine(json.dumps({'newplayer':p.toJSON()}))

    def buildProtocol(self, addr):
        return BoomProtocol(self)

    def processData(self, data):
        data = json.loads(data)
        for u in self.users:
            if u.pid == data['pid']:
                u.acceptCommands(data['actions'])

    def broadcast(self):
        player_list = self.playerList()
        for u in self.users:
            u.boom.sendLine(json.dumps({"player_list":player_list}))

    def playerList(self):
        player_list = {}
        for p in self.users:
            player_list[p.pid] = p.toObj()
        return player_list

f = GameFactory()
s = SockJSFactory(f)

reactor.listenTCP(8090, s)

lc = LoopingCall(f.broadcast)
lc.start(0.03333333333333)

reactor.run()



