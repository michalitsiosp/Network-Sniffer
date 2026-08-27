import subprocess #for Nmap
import urllib.request #for api
import sys #for pre run input
import time
from scapy.all import srp, Ether, ARP, conf, IP, sr, ICMP , get_if_addr
import logging
logging.getLogger("scapy").setLevel(logging.CRITICAL)
conf.verb = 0
print(r"  _   _      _                      _       _____       _  __  __          ")
print(r" | \ | |    | |                    | |     / ____|     (_)/ _|/ _|         ")
print(r" |  \| | ___| |___      _____  _ __| | __ | (___  _ __  _| |_| |_ ___ _ __ ")
print(r" | . ` |/ _ \ __\ \ /\ / / _ \| '__| |/ /  \___ \| '_ \| |  _|  _/ _ \ '__|")
print(r" | |\  |  __/ |_ \ V  V / (_) | |  |   <   ____) | | | | | | | ||  __/ |   ")
print(r" |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\ |_____/|_| |_|_|_| |_| \___|_|   ")
print(r"                                                                           ")
#traceroute.py

def traceroute():





	target = input("write target ip: ")

	print(f"[*] Tracing route to {target}\n")
	print("TTL\tRouter/IP\t\tResponse")
	print("-" * 55)

	ping = False
	ttl = 1
	while ping == False and ttl != 30:
        	ans,unans=sr(IP(dst=target, ttl=ttl)/ICMP(),timeout = 1)
        	for sent, received in ans:
                	print(f"{sent.ttl}\t{received.src}\t\t{received.summary()}")
                	if received.type == 0:
                        	ping = True
                        	break
        	ttl=ttl+1
       		time.sleep(0.2)
	if not ping:
    		print("\n[-] Target was not reached within the TTL limit.")

#find device
def get_vendor(mac_address):
    try:
        url = f"https://api.macvendors.com/{mac_address}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.read().decode('utf-8')
    except:
        return "Unknown Vendor"


#netdiscover.py
def netdiscover():
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
	print("IP Address\t\tMAC Address\t\tDevice")
	print("-" * 65)

	for sent, received in answered:
    		vendor = get_vendor(received.hwsrc)
    		print(f"{received.psrc:<16}\t{received.hwsrc}\t{vendor}")
    		time.sleep(1)

def nmap_scan():
    target = input("Enter target IP or Network (e.g., 192.168.1.1): ").strip()
    
    print("\nSelect Scan Type:")
    print("1. Quick Scan (Fast Top Ports)")
    print("2. Service & Script Scan (Standard -sV -sC)")
    print("3. Aggressive OS & Port Scan (Comprehensive -A -T4)")
    print("4. Full stealth Scan all ports -sS -p- -Pn --max-rate 100 -T2") 
    ap = input("\nEnter choice (1-4): ").strip()

    # Συγκρίνουμε με strings ("1", "2", "3") και όλα είναι μέσα στη συνάρτηση
    if ap == "1":
        print(f"\n[*] Starting Quick Scan on {target}...\n")
        args = ["nmap", "-F", target]
    elif ap == "2":
        print(f"\n[*] Starting Service & Script Scan on {target}...\n")
        args = ["sudo","nmap", "-sV", "-sC", target]
    elif ap == "3":
        print(f"\n[*] Starting Aggressive Scan on {target}...\n")
        args = ["sudo,""nmap", "-A", "-T4", target]
    else:
        print(f"\n[*] Starting Full Stealth Scan on {target}\n")
        args = ["sudo","nmap", "-sS", "-p-", "-Pn", "--max-rate", "100", "-T2", target]

    try:
        subprocess.run(args, check=True)
    except FileNotFoundError:
        print("[-] Error: Nmap is not installed or not in PATH.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error executing Nmap: {e}")
    except KeyboardInterrupt:
        print("\n[-] Scan cancelled by user.")#selection menu 

def main():
	while True:
		print("**MENU**")
		print("1. Netdiscover")
		print("2. Traceroute")
		print("3. Nmap Scan")
		print("4. Exit")
		apanthsh = int(input("Select from (1-4): "))
		if apanthsh == 1:
			netdiscover()
			for i in range(1,4):
                                print("-" * 65)
                                print("-" * 65)

		elif apanthsh == 2:
			traceroute()
			for i in range(1,4):
				print("-" * 65)
				print("-" * 65)
		elif apanthsh == 3:
			nmap_scan()
		else:
			print("--Exit--")
			break

if __name__=="__main__":
	main()


