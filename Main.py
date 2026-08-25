import sys
import time
from scapy.all import srp, Ether, ARP, conf, IP, sr, ICMP , get_if_addr
import logging
logging.getLogger("scapy").setLevel(logging.CRITICAL)
conf.verb = 0

#traceroute.py
if len(sys.argv) != 2:
	print("Usage: python script.py <target>\n eg: python script.py google.com")
	sys.exit(1)




target = sys.argv[1]

print(f"[*] Tracing route to {target}\n")
print("TTL\tRouter/IP\t\tResponse")
print("-" * 55)

ping = False
ttl = 1
while ping == False and ttl != 30:
        ans,unans=sr(IP(dst=sys.argv[1], ttl=ttl)/ICMP(),timeout = 1)
        for sent, received in ans:
                print(f"{sent.ttl}\t{received.src}\t\t{received.summary()}")
                if received.type == 0:
                        ping = True
                        break
        ttl=ttl+1
        time.sleep(0.2)
if not ping:
    print("\n[-] Target was not reached within the TTL limit.")

#netdiscover.py
my_ip = get_if_addr(conf.iface)  # returns eg "192.168.55.12"
target1 = ".".join(my_ip.split(".")[:-1]) + ".0/24"  
try:
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request = ARP(pdst=target1)
    packet = broadcast / arp_request
    answered, unanswered = srp(packet, timeout=3, verbose=0)
except Exception as e:
    print(f"[-] Error: {e} ")
    sys.exit(1)
print("IP Address\t\tMAC Address")
print("-" * 40)

for sent, received in answered:
    print(f"{received.psrc}\t\t{received.hwsrc}")
