from txsockjs.factory import SockJSFactory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Factory, ClientFactory, Protocol
from twisted.protocols.basic import LineReceiver
import time

import json

from twisted.internet import reactor, protocol



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
        self.factory.users.remove(self)
        

class GameFactory(Factory):

    def __init__(self):
        self.users = set()

    def addUser(self, user):
        self.users.add(user)
        for u in self.users:
            u.sendLine(json.dumps({'newplayer':{'x':300, 'y':300}}))

    def buildProtocol(self, addr):
        return BoomProtocol(self)

    def processData(self, data):
        return
        #self.emit(json.dumps(self.data))

    def broadcast(self):
        for u in self.users:
            u.sendLine(json.dumps({'timed':'broadcast'}))

    def emit(self, message):
        for u in self.users:
            u.sendLine(message)

f = GameFactory()
s = SockJSFactory(f)

reactor.listenTCP(8090, s)

lc = LoopingCall(f.broadcast)
lc.start(0.5)

reactor.run()



