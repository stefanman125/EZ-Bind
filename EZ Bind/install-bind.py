#!/usr/bin/python3
import subprocess
import os

os.system("yum install bind bind-utils")

domain_name = input("Enter a domain name: ")
hostname = input("Enter an FQDN (this will change the hostname of the server): ")
os.system("hostnamectl set-hostname "+hostname)

ip = input("Enter the IP address you want the DNS server to listen on (USE CIDR FORMAT): ").split('/')
os.system("sed 's/$IP_ADDR/" + ip[0] + "/g' configuration\ files/named.conf > /etc/named.conf")

os.system("mkdir /etc/named/")
reverse_ip = '.'.join(ip[0].split('.')[::-1][-int(4-(32-int(ip[1]))/8):])
subnet_ip = '.'.join(ip[0].split('.')[:-int(4-(32-int(ip[1]))/8)])
os.system("sed 's/$FQDN/" + domain_name + "/g; s/$REVERSE_IP/" + reverse_ip + "/g; s/$SUBNET_IP/" + subnet_ip + "/g' configuration\ files/named.conf.local > /etc/named/named.conf.local")

os.system("mkdir /etc/named/zones/")
reversed_host_bits = '.'.join(ip[0].split('.')[-int(4-int(ip[1])/8):])
os.system("sed 's/$HOSTNAME/" + hostname + "/g; s/$FQDN/" + domain_name + "/g; s/$IP_ADDR/" + ip[0] + "/g; s/$REVERSED_HOST_BITS/" + reversed_host_bits + "/g;' configuration\ files/db.SUBNET_IP > /etc/named/zones/db." + subnet_ip)

os.system("sed 's/$HOSTNAME/" + hostname + "/g; s/$FQDN/" + domain_name + "/g; s/$IP_ADDR/" + ip[0] + "/g; s/$IP_SUBNET/" + ip[1] + "/g;' configuration\ files/db.FQDN > /etc/named/zones/db." + domain_name)
print("Remember to add A records to /etc/db." + domain_name)

print("named-checkconf:")
os.system("named-checkconf")

print("checking forward zone:")
os.system("named-checkzone " + domain_name + " /etc/named/zones/db." + domain_name)

print("checking reverse zone:")
os.system("named-checkzone " + reverse_ip + ".in-addr.arpa /etc/named/zones/db." + subnet_ip)

os.system("systemctl restart named")
os.system("systemctl enable named")

os.system("firewallcmd --permanent --add-port 53/tcp")
os.system("firewallcmd --permanent --add-port 53/udp")
os.system("firewallcmd --reload")

print("Make sure to add this to each host's resolv.conf:\nsearch " + domain_name + "\nnameserver " + ip[0])

