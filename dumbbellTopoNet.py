#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class dumbbellTopo(Topo):
    "2 backbone routers, 2 access routers, 2 hosts each side."
    def build(self):
        #backbone routers
        backBoneRouter1 = self.addSwitch('bbR1')
        backBoneRouter2 = self.addSwitch('bbR2')
        
        #access routers
        accessRouter1 = self.addSwitch('aR1')
        accessRouter2 = self.addSwitch('aR2')

        #hosts
        sourceHost1 = self.addHost('sH1')
        sourceHost2 = self.addHost('sH2')
        receiverHost1 = self.addHost('rH1')
        receiverHost2 = self.addHost('rH2')
        
        #links
        self.addLink(backBoneRouter1, backBoneRouter2)
        self.addLink(accessRouter1, backBoneRouter1)
        self.addLink(accessRouter2, backBoneRouter2)
        
        self.addLink(sourceHost1, accessRouter1)
        self.addLink(sourceHost2, accessRouter1)
        self.addLink(receiverHost1, accessRouter2)
        self.addLink(receiverHost2, accessRouter2)


def simpleTest():
    "Create and test a simple network"
    #topo = SingleSwitchTopo(n=4)
    topo = dumbbellTopo()
    net = Mininet(topo)
    net.start()
    print( "Dumping host connections" )
    dumpNodeConnections(net.hosts)
    print( "Testing network connectivity" )
    net.pingAll()
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
