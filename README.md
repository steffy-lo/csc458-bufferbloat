This assignment involves studying the dynamics of TCP in home networks as follows:
Within Mininet, the following topology is to be created. 
Here h1 is a home computer that has a fast connection (1Gb/s) to a home router with a slow uplink connection (10Mb/s). 
The round-trip propagation delay, or the minimum RTT between h1 and h2 is 4ms. 
The router buffer size can hold 100 full sized ethernet frames (about 150kB with an MTU of 1500 bytes).

Then the following steps are implemented:
1. Start a long lived TCP flow sending data from h1 to h2. Use iperf.
2. Send pings from h1 to h2 10 times a second and record the RTTs.
3. Plot the time series of the following:
	- The long lived TCP flow’s cwnd
	- The RTT reported by ping
	- Queue size at the bottleneck
4. Spawn a webserver on h1. Periodically download the index.html web page (three times every five seconds) from h1 and measure how long it takes to fetch it (on average).
The long lived flow, ping train, and webserver downloads should all be happening simultaneously.
The above experiment is then repeated with a smaller router buffer size (Q=20 packets).

# Instructions
Please begin by installing the statistics module by running "sudo pip install statistics".
Next, run a single shell command "sudo ./run.sh". This should produce 6 plots:
3 each for router buffer sizes 100 and 20 packets and a results.txt containing the average and std dev
for the fetch results.
Note: The results.txt is in w+ mode so need to check for the result appended for the first run (bb-q20),
before it gets overwritten with the second run results (bb-q100). A previous_results.txt is included
that contains the results for one of the runs.

1. Why do you see a differences in webpage fetch times with short and large router buffers?

   One of the runs had results as follows:
	bb-q20
	average: 0.504805555556
	std dev: 0.074230540264

	bb-q100
	average: 1.11019047619
	std dev: 0.581217330144

   As we can see, the average fetch times for the short router buffer is shorter than that of the long
   router buffer. This is likely due to excess buffering of packets in the queue. Because the short router
   buffer will have a shorter queue, the number of packets queued is less resulting in a shorter wait time.

2. What is the (max) transmit queue length on the network interface reported by ifconfig?
   For this queue size, if you assume the queue drains at 100Mb/s, what is the maximum time
   a packet might wait in the queue before it leaves the NIC?

   txqueuelen: 1000

   This means that when the queue is full, it would hold 1,500,000 (1000*1500) byte packets.
   Therefore, the maximum time a packet would have to wait before it leaves the NIC is:

   1000 * 1500 * 8 * 1/(100*10^6) = 0.12s

3. How does the RTT reported by ping vary with the queue size? Write a symbolic equation to
   describe the relation between the two.

	Just from looking at the graphs, RTT is clearly directly proportional to queue size.
	Therefore, we can write this as: RTT = k * qsize.

4. Identify and describe two ways to mitigate the bufferbloat problem.

	The first and most straightforward way is to simply reduce the queue size by having a
	shorter router buffer. The second way is to somehow tweak the flow of traffic such that
	we are limiting the rate of traffic although at a cost of lower bandwidth.
