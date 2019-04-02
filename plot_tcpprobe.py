from helper import *
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--sport', help="Enable the source port filter (Default is dest port)", action='store_true', dest="sport", default=False)
parser.add_argument('-p', '--port', dest="port", default='5001')
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
parser.add_argument('-H', '--histogram', dest="histogram",
                    help="Plot histogram of sum(cwnd_i)",
                    action="store_true",
                    default=False)

args = parser.parse_args()

def first(lst):
    return map(lambda e: e[0], lst)

def second(lst):
    return map(lambda e: e[1], lst)

"""
Sample line:
(pre-Linux 3.12):
2.221032535 10.0.0.2:39815 10.0.0.1:5001 32 0x1a2a710c 0x1a2a387c 11 2147483647 14592 85
(post-Linux 3.12):
0.004313854 192.168.56.101:22 192.168.56.1:57321 32 0xa34f92b0 0xa34f9240 10 2147483647 131024 1 43520

source code: http://lxr.free-electrons.com/source/net/ipv4/tcp_probe.c?v=3.12
0: Time in seconds
1: Source IP:Port
2: Dest IP: Port
3: Packet length (bytes)
4: snd_nxt
5: snd_una
6: snd_cwnd
7: ssthr
8: snd_wnd
9: srtt
10: rcv_wnd (3.12 and later)
"""
def parse_file(f):
    num_fields = 10
    linux_ver = os.uname()[2].split('.')[:2] # example '3.13.0-24-generic' 
    ver_1, ver_2 = [int(ver_i) for ver_i in linux_ver]
    if ver_1 == 3 and ver_2 >= 12:
        num_fields = 11

    times = defaultdict(list)
    cwnd = defaultdict(list)
    srtt = []
    for l in open(f).xreadlines():
        fields = l.strip().split(' ')
        if len(fields) != num_fields:
            break
        if not args.sport:
            if fields[2].split(':')[1] != args.port:
                continue
        else:
#            print "using sport %s (compare with %s)" % (args.port, fields[1].split(':')[1])
            if fields[1].split(':')[1] != args.port:
                continue
        sport = int(fields[1].split(':')[1])
        times[sport].append(float(fields[0]))

        c = int(fields[6])
        cwnd[sport].append(c * 1480 / 1024.0)
        srtt.append(int(fields[-1]))
    return times, cwnd

added = defaultdict(int)
events = []

def plot_cwnds(ax):
    global events
    for f in args.files:
        times, cwnds = parse_file(f)
        for port in sorted(cwnds.keys()):
            t = times[port]
            cwnd = cwnds[port]

            events += zip(t, [port]*len(t), cwnd)
            ax.plot(t, cwnd)

    events.sort()
total_cwnd = 0
cwnd_time = []

min_total_cwnd = 10**10
max_total_cwnd = 0
totalcwnds = []

m.rc('figure', figsize=(16, 6))
fig = plt.figure()
plots = 1
if args.histogram:
    plots = 2

axPlot = fig.add_subplot(1, plots, 1)
plot_cwnds(axPlot)

for (t,p,c) in events:
    if added[p]:
        total_cwnd -= added[p]
    total_cwnd += c
    cwnd_time.append((t, total_cwnd))
    added[p] = c
    totalcwnds.append(total_cwnd)

axPlot.plot(first(cwnd_time), second(cwnd_time), lw=2, label="$\sum_i W_i$")
axPlot.grid(True)
#axPlot.legend()
axPlot.set_xlabel("seconds")
axPlot.set_ylabel("cwnd KB")
axPlot.set_title("TCP congestion window (cwnd) timeseries")

if args.histogram:
    axHist = fig.add_subplot(1, 2, 2)
    n, bins, patches = axHist.hist(totalcwnds, 50, normed=1, facecolor='green', alpha=0.75)

    axHist.set_xlabel("bins (KB)")
    axHist.set_ylabel("Fraction")
    axHist.set_title("Histogram of sum(cwnd_i)")

if args.out:
    print 'saving to', args.out
    plt.savefig(args.out)
else:
    plt.show()
