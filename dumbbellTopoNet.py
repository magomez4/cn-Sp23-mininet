#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from time import sleep
from plot_output import plot_bandwidth, plot_congestion

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
       
        #link speeds (in p/ms)
        backBoneSpeedpms = 82
        accessSpeedpms = 21
        srcSpeedpms = 80
        rcvSpeedpms = 80

        #link speeds (in Mbps)
        msToSec = 1000
        bitsPerPacket = 12000 #a regular 1500byte packet has 1500*8 = 12000 bits
        bitsToMegabits = 0.000001
        conversionFactor = msToSec * bitsPerPacket * bitsToMegabits
        backBoneSpeed = backBoneSpeedpms * conversionFactor #984Mbps
        accessSpeed = accessSpeedpms * conversionFactor #252Mbps
        srcSpeed = srcSpeedpms * conversionFactor #960Mbps
        rcvSpeed = rcvSpeedpms * conversionFactor #960Mbps


        #propagation delays (in ms)
        shortDelay = 21
        mediumDelay = 81
        longDelay = 162
        currentDelay = shortDelay #this can be changed to test different cases

        #links
        arLinkConfig = dict(bw=accessSpeed, max_queue_size=0.2*accessSpeed*currentDelay)
        bbLinkConfig = dict(bw=backBoneSpeed, delay=currentDelay)
        srcLinkConfig = dict(bw=srcSpeed)
        rcvLinkConfig = dict(bw=rcvSpeed)
        self.addLink(backBoneRouter1, backBoneRouter2, **bbLinkConfig)
        self.addLink(accessRouter1, backBoneRouter1, **arLinkConfig)
        self.addLink(accessRouter2, backBoneRouter2, **arLinkConfig)
        self.addLink(sourceHost1, accessRouter1, **srcLinkConfig)
        self.addLink(sourceHost2, accessRouter1, **srcLinkConfig)
        self.addLink(receiverHost1, accessRouter2, **rcvLinkConfig)
        self.addLink(receiverHost2, accessRouter2, **rcvLinkConfig)



def simpleTest():
    "Create and test a simple network"
    topo = dumbbellTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    print( "Dumping host connections" )
    dumpNodeConnections(net.hosts)
    print( "Testing network connectivity" )
    net.pingAll()

    source1 = net.get('sH1')
    receiver1 = net.get('rH1')

    print("starting iperf3 on receiver 1")
    #receiver1.cmd('nohup iperf3 -s -p 5566 -i 1 > client.txt &')
    receiver1.cmd('nohup iperf3 -s -p 5566 -i 1 > server.txt &')
    # nohup iperf3 -s -p $port > $out.client &

    #t = 500
    t = 15
    print("starting iperf3 on source 1")
    rcv1IP = receiver1.IP()
    #source1.sendCmd(f"nohup iperf3 -V -4 -i 1 -f m -d -c {rcv1IP} -p 5566 -t {t} > server.txt")
    source1.cmd(f"nohup iperf3 -c {rcv1IP} -p 5566 -t {t} > client.txt &")
    #  nohup iperf3 -V -4 -i 1 -f m -d -t $time -c $server -p $port > $out.server &
    
    print("waiting for outputs...")
    #src1Output = source1.waitOutput()
    sleep(t+2) 
    
    print("killing server...")
    killResult = receiver1.cmd('kill %iperf3')
    
    print(f"done with test...killResult = {killResult}")
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
    #plot_bandwidth('client.txt')
    #plot_congestion('client.txt')
