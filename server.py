from twisted.internet.protocol import Factory
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor

class Game(Protocol):
    def __init__(self,players):
        self.players = players
        self.name = None
        self.state = "ADDPLAYER"

    def connectionMade(self):
        ## prompt player to add player info (i.e name?)


    def connectionLost(self,reason):
        if self.name in self.users:
            del self.users[self.name]

    def dataReceived(self,data):
        if self.state == "ADDPLAYER":
            self.handle_ADDPLAYER(data)

        else:
            self.handle_PLAY(data)

    def handle_ADDPLAYER(self,data):
        ## data received is used for creating a new player in the game
        ## set name
        self.users[name] = self
        self.state = "PLAY"

    def handle_PLAY(self,data):
        for name, protocol in self.users.iteritems():
            if protocol != self:
                protocol.transport.write(data)


class GameFactory(Factory):
    def __init__(self):
        self.players = {}

    def buildProtocol(self,addr):
        return Game(self.players)

reactor.listenTCP(9001, GameFactory())
reactor.run()
