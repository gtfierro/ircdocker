import re
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from datetime import datetime
from collections import defaultdict

last_seen = {}
tell_messages = defaultdict(list)

def say_hi_back(helloword, msg, username):
    return helloword + ' ' + username + '!'

def get_last_seen(seen, msg, username):
    search_name = msg.split(seen)[1].strip()
    if search_name not in last_seen:
        return "I haven't seen {0} before".format(search_name)
    return "I last saw {0} at {1}".format(search_name, last_seen[search_name])

def tell_user(tell, msg, username):
    tell_name = msg.split(tell,1)[1].split()[0]
    message = msg.split(tell_name,1)[1]
    tell_messages[tell_name].append("{0} @ {1} : {2}".format(username, datetime.now(), message))
    return "I will tell {0} that when they come back".format(tell_name)

def print_help(*args):
    return """
<< (hi|hello|hey) ripley >>
  ripley will say hi back

<< ripley: tell username message message message >>
  you can queue up multiple messages to [username] that are delivered when [username] next appears

<< ripley: last seen username >>
<< ripley: seen username >>
  will print out in local time when [username] was last seen
"""


responses = {}

responses['(hi|hello|hey)'] = say_hi_back
responses['(last )?seen'] = get_last_seen
responses['tell'] = tell_user
responses['help'] = print_help

def find_match(text):
    for resp in responses:
        match = re.compile(resp, re.I).match(text)
        if match:
            return responses[resp], match.group()
    return None, None


class RipleyBot(irc.IRCClient):

    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as {0}".format(self.nickname)

    def joined(self, channel):
        print "Joined {0}".format(channel)

    def privmsg(self, user, channel, msg):
        print user, channel, msg, self.nickname
        if not user:
            return
        user = user.split('!',1)[0]

        last_seen[user] = datetime.now()

        if user in tell_messages:
            self.msg(self.factory.channel, "OI {0}, you have messages!".format(user.upper()))
            for message in tell_messages[user]:
                self.msg(self.factory.channel, message)
            del tell_messages[user]

        if self.nickname in msg:
            msg = re.compile(self.nickname + '[:,]* ?', re.I).sub('',msg)
            f, group = find_match(msg)
            if f:
                response = f(group, msg, user)
                self.msg(self.factory.channel, response)

class RipleyFactory(protocol.ClientFactory):
    protocol = RipleyBot

    def __init__(self, channel, nickname="ripley"):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection {0}, reconnecting...".format(reason)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: {0}".format(reason)



if __name__=='__main__':
    reactor.connectTCP('server',6667,RipleyFactory('#chatroom'))
    reactor.run()
