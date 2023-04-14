import re
import pandas as pd
import matplotlib.pyplot as plt


class Row():
    def __init__(self, line, offset=0):
        self._parse_transfer(line)
        self._parse_interval(line, offset)
        self._parse_bandwidth(line)
        
    def __str__(self):
        return f'{str(self.interval_end):>6} sec {self.transfer:>6} GBytes {self.bandwidth:>6} Gbits/sec'
    
    @property
    def is_valid(self):
        return self.interval_start is not None
    
    def _parse_transfer(self, line):
        # change
        m = re.search('([0-9\.]+)\s+?([MG]Bytes)', line)
        self.transfer = float(m.group(1)) if m else None
        self.transfer_unit = m.group(2) if m else None
    
    def _parse_interval(self, line, offset):
        m = re.search('([0-9\.]+)-\s?([0-9\.]+)\s+?sec', line)
        self.interval_start = (float(m.group(1)) + offset) if m else None
        self.interval_end = (float(m.group(2)) + offset) if m else None
    
    def _parse_bandwidth(self, line):
        m = re.search('([0-9\.]+)\s+?([MG]bits/sec)', line)
        self.bandwidth = float(m.group(1)) if m else None
        self.bandwidth_unit = m.group(2) if m else None



def read_output_file(file_name, offset=0):
    for line in open(file_name):
        row = Row(line, offset)
        if row.is_valid:
            yield row
        

def plot_congestion(file_name):
    data = [row.__dict__ for row in read_output_file(file_name)]
    df = pd.DataFrame(data=data)
    df.plot(kind='line', 
            x='interval_end', 
            y='transfer', 
            xlabel='Time in (sec)', 
            ylabel=f'Congestion Window in ({data[0]["transfer_unit"]})',
            style='-')
    plt.ylim(0)
    plt.xlim(0)
    plt.savefig(f'{file_name}-congestion.png', bbox_inches='tight')

def plot_bandwidth(algo):
    s1 = [row.__dict__ for row in read_output_file(f'{algo}/s1.txt')]
    s2 = [row.__dict__ for row in read_output_file(f'{algo}/s2.txt', offset=50)]
    df = pd.DataFrame(data=s1)
    ax = df.plot(kind='line', 
            x='interval_end', 
            y='bandwidth', 
            xlabel='Time in (sec)',
            ylabel=f'Bandwidth in ({s1[0]["bandwidth_unit"]})',
            style='-')
    df2 = pd.DataFrame(data=s2)
    df2.plot(ax=ax,
            x='interval_end', 
            y='bandwidth')

    ax.legend(['h1 to h3', 'h2 to h4'])
    plt.ylim(0)
    plt.xlim(0)
    plt.savefig(f'{algo}/bandwidth.png', bbox_inches='tight')

if __name__ == '__main__':
    plt.rcParams["figure.figsize"] = (16,8)
    plot_bandwidth('reno')
    