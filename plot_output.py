import re
import pandas as pd
import matplotlib.pyplot as plt


class Row():
    def __init__(self, line):
        self.transfer = Row._parse_transfer(line)
        self.interval_start, self.interval_end = Row._parse_interval(line)
        self.bandwidth = Row._parse_bandwidth(line)
        
    def __str__(self):
        return f'{str(self.interval_end):>6} sec {self.transfer:>6} GBytes {self.bandwidth:>6} Gbits/sec'
    
    @classmethod
    def valid_row(cls, line):
        return Row._parse_transfer(line) is not None
    
    @classmethod
    def _parse_transfer(cls, line):
        m = re.search('([0-9\.]+) GBytes', line)
        return float(m.group(1)) if m else None
    
    @classmethod
    def _parse_interval(cls, line):
        m = re.search('([0-9\.]+)-\s?([0-9\.]+) sec', line)
        return (float(m.group(1)), float(m.group(2))) if m else None
    
    @classmethod
    def _parse_bandwidth(cls, line):
        m = re.search('([0-9\.]+) Gbits/sec', line)
        return float(m.group(1)) if m else None



def read_output_file(file_name):
    for line in open(file_name):
        if Row.valid_row(line):
            yield Row(line)
        


if __name__ == '__main__':
    data = [row.__dict__ for row in read_output_file('sample_output.txt')][:-1]
    df = pd.DataFrame(data=data)
    df.plot(kind='line', 
            x='interval_end', 
            y='bandwidth', 
            xlabel='time (sec)', 
            ylabel='throughput (Gbps)',
            style='-o')
    plt.ylim(0)
    plt.savefig('bandwidth.png')
    