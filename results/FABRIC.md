# Measured direct-fabric results

The head and worker negotiated a 200,000 Mb/s full-duplex link over their direct
ConnectX-7 interfaces. The benchmark used four TCP streams for 15 seconds in
each direction, followed by 1,000 8 MiB RDMA writes using RoCE v2 GID index 3.

| Test | Result |
| --- | ---: |
| Head → worker TCP | 95.35 Gb/s received |
| Worker → head TCP | 90.36 Gb/s received |
| RDMA write average | 108.98 Gb/s |
| Ping average | 0.939 ms |
| Link MTU during test | 1500 bytes |

The model replication command targeted the worker's `10.100.10.2` fabric
address. Route inspection proved that rsync/SSH used the direct cable rather
than LAN or Tailscale. It transferred 173,766,905,451 bytes
in 536 seconds (0.302 GiB/s). That lower application rate reflects
single-stream SSH encryption, rsync, and concurrent disk work; it is not the
fabric's measured capacity.

Raw evidence:

- [Forward iperf3 JSON](raw/fabric/20260719T162733Z/iperf3-forward.json)
- [Reverse iperf3 JSON](raw/fabric/20260719T162733Z/iperf3-reverse.json)
- [RDMA client output](raw/fabric/20260719T162733Z/ib-write-bw-client.txt)
- [RDMA server output](raw/fabric/20260719T162733Z/ib-write-bw-server.txt)
- [Ping output](raw/fabric/20260719T162733Z/ping.txt)

TCP showed substantial retransmits at MTU 1500. Jumbo-MTU and transfer-tool
tuning remain follow-up experiments; they were not changed after measurement.
