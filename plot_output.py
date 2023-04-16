import sys
import re
import pandas as pd
import matplotlib.pyplot as plt


class Row():
    def __init__(self, line, offset=0):
        self._parse_cwnd(line)
        self._parse_interval(line, offset)
        self._parse_bandwidth(line)

    def __str__(self):
        return f'{str(self.interval_end):>6} sec {self.cwnd:>6} KBytes {self.bandwidth:>6} Mbits/sec'

    @property
    def is_valid(self):
        return self.interval_start is not None and self.cwnd is not None and self.bandwidth is not None

    def _parse_cwnd(self, line):
        '''Cwnd in KBytes'''
        m = re.search('([0-9\.]+)\s+?([KM]Bytes)\s+?$', line)
        unit = m.group(2) if m else None
        cwnd = float(m.group(1)) if m else None
        
        self.cwnd = None
        if cwnd is not None:
            self.cwnd = 1000 * cwnd if (unit == 'MBytes') else cwnd


    def _parse_interval(self, line, offset):
        m = re.search('([0-9\.]+)-\s?([0-9\.]+)\s+?sec', line)
        self.interval_start = (float(m.group(1)) + offset) if m else None
        self.interval_end = (float(m.group(2)) + offset) if m else None

    def _parse_bandwidth(self, line):
        '''Bitrate in Mbits/sec'''
        m = re.search('([0-9\.]+)\s+?([MG]bits/sec)', line)
        bandwidth = float(m.group(1)) if m else None
        unit = m.group(2) if m else None
        
        self.bandwidth = None
        if bandwidth is not None:
            self.bandwidth = 1000 * bandwidth if (unit == 'Gbits/sec') else bandwidth


def read_output_file(file_name, offset=0):
    for line in open(file_name):
        row = Row(line, offset)
        if row.is_valid:
            yield row


def plot_congestion(algo, delay):
    s1 = [row.__dict__ for row in read_output_file(f'{algo}/s1.txt')]
    s2 = [row.__dict__ for row in read_output_file(
        f'{algo}/s2.txt', offset=delay)]
    df = pd.DataFrame(data=s1)
    ax = df.plot(kind='line',
                 x='interval_end',
                 y='cwnd',
                 xlabel='Time in (sec)',
                 ylabel=f'Congestion Window in (KBytes)',
                 style='-')
    df2 = pd.DataFrame(data=s2)
    df2.plot(ax=ax,
             x='interval_end',
             xlabel='Time in (sec)',
             y='cwnd')
    ax.legend(['h1 to h3', 'h2 to h4'])
    plt.ylim(0)
    plt.xlim(0)
    plt.savefig(f'{algo}/cwnd.png', bbox_inches='tight')


def plot_bandwidth(algo, dealy):
    s1 = [row.__dict__ for row in read_output_file(f'{algo}/s1.txt')]
    s2 = [row.__dict__ for row in read_output_file(
        f'{algo}/s2.txt', offset=delay)]
    df = pd.DataFrame(data=s1)
    ax = df.plot(kind='line',
                 x='interval_end',
                 y='bandwidth',
                 xlabel='Time in (sec)',
                 ylabel=f'Bandwidth in (Mbits/sec)',
                 style='-')
    df2 = pd.DataFrame(data=s2)
    df2.plot(ax=ax,
             x='interval_end',
             xlabel='Time in (sec)',
             y='bandwidth')

    ax.legend(['h1 to h3', 'h2 to h4'])
    plt.ylim(0)
    plt.xlim(0)
    plt.savefig(f'{algo}/bandwidth.png', bbox_inches='tight')


if __name__ == '__main__':
    algorithm = 'reno' if len(sys.argv) <= 1 else sys.argv[1]
    delay = 250 if len(sys.argv) <= 2 else int(sys.argv[2])
    print(f'Plotting algorithm {algorithm} widh delay {delay}')

    plt.rcParams["figure.figsize"] = (16,8)
    plot_bandwidth(algorithm, delay)
    plot_congestion(algorithm, delay)
