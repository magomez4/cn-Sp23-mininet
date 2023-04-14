#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections, quietRun
from mininet.log import setLogLevel
from time import sleep
from plot_output import plot_bandwidth, plot_congestion


def pms_to_mbps(pms):
    # sec/ms x bits/packet x Megabits/bit
    factor = 1000 * 12000 * 0.000001
    return pms * factor


def set_tcp_congestion_control(algorithm):
    quietRun(f'sysctl -w net.ipv4.tcp_congestion_control={algorithm}')


class DumbbellTopo(Topo):
    def build(self):
        '''2 backbone routers, 2 access routers, 2 hosts each side.'''

        # Backbone routers
        bb_r1 = self.addSwitch('bbR1')
        bb_r2 = self.addSwitch('bbR2')

        # Access routers
        a_r1 = self.addSwitch('aR1')
        a_r2 = self.addSwitch('aR2')

        # Hosts
        s_h1 = self.addHost('sH1')
        s_h2 = self.addHost('sH2')
        r_h1 = self.addHost('rH1')
        r_h2 = self.addHost('rH2')

        # link speeds (in Mbps)
        bb_speed = pms_to_mbps(82)  # 984Mbps
        a_speed = pms_to_mbps(21)  # 252Mbps
        r_speed = s_speed = pms_to_mbps(80)  # 960Mbps

        # Propagation delays (in ms)
        small, medium, large = 21, 81, 162
        delay = small  # This can be changed to test different cases

        # Links
        ar_link = dict(bw=a_speed, max_queue_size=0.2 * a_speed * delay)
        bb_link = dict(bw=bb_speed, delay=delay)
        s_link = dict(bw=s_speed)
        r_link = dict(bw=r_speed)

        self.addLink(bb_r1, bb_r2, **bb_link)
        self.addLink(a_r1, bb_r1, **ar_link)
        self.addLink(a_r2, bb_r2, **ar_link)
        self.addLink(s_h1, a_r1, **s_link)
        self.addLink(s_h2, a_r1, **s_link)
        self.addLink(r_h1, a_r2, **r_link)
        self.addLink(r_h2, a_r2, **r_link)


def execute(algo='reno', duration=500, delay=250):

    set_tcp_congestion_control(algo)

    setLogLevel('info')
    topo = DumbbellTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    dumpNodeConnections(net.hosts)

    processes = {}

    # H1 -> H3
    s_1 = net.get('sH1')
    r_1 = net.get('rH1')

    # H2 -> H4
    s_2 = net.get('sH2')
    r_2 = net.get('rH2')

    # Start a server on both receivers
    processes[r_1] = r_1.popen(f'nohup iperf3 -s -p 1111 -i 1 &', shell=True)
    processes[r_2] = r_2.popen(f'nohup iperf3 -s -p 2222 -i 1 &', shell=True)

    # Start source 1
    processes[s_1] = s_1.popen(
        f'nohup iperf3 -4 -i 1 -f m -t {duration} -c {r_1.IP()} -p 1111 > {algo}/s1.txt &', shell=True)

    # Start source 2
    sleep(delay)
    duration -= delay
    processes[s_2] = s_2.popen(
        f'nohup iperf3 -4 -i 1 -f m -t {duration} -c {r_2.IP()} -p 2222 > {algo}/s2.txt &', shell=True)

    sleep(duration)

    # Wait for all processes to finish
    processes[s_1].wait()
    processes[s_2].wait()

    processes[r_1].terminate()
    processes[r_2].terminate()

    processes[r_1].wait()
    processes[r_2].wait()

    net.stop()


if __name__ == '__main__':
    execute()
