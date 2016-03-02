# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import sys
import time
import pexpect
import base

from termcolor import colored, cprint


class DebianBox(base.BaseDevice):
    '''
    A linux machine running an ssh server.
    '''

    prompt = ['root\\@.*:.*#', '/ # ', ".*:~ #" ]

    def __init__(self,
                 name,
                 color,
                 output=sys.stdout,
                 username=None,
                 password=None,
                 port=None,
                 reboot=False,
                 location=None,
                 ifconfig_cmd=None,
                 aptget_cmd=None,
                 route_cmd=None,
                 dhclient_cmd=None,
                 ip_cmd=None,
                 iptables_cmd=None,
                 isc_dhcp_server_cmd=None,
                 tiny_proxy_cmd=None,
                 tftpd_hpa_cmd=None,
                 reboot_cmd=None,
                 killall_cmd=None,
                 sysctl_cmd=None,
                 delete_dhcp_client_leases_cmd=None,
                 write_to_dhcpd=None
                 ):
        if name is None:
            return
        if username is None:
            username='root'
        if password is None:
            password='bigfoot1'
        if port is None:
            port='22'

        if ifconfig_cmd is None:
            ifconfig_cmd="sudo ifconfig"
        if aptget_cmd is None:
            aptget_cmd="sudo apt-get"
        if route_cmd is None:
            route_cmd = "sudo route"
        if dhclient_cmd is None:
            dhclient_cmd = "sudo dhclient"
        if ip_cmd is None:
            ip_cmd = "sudo ip"
        if iptables_cmd is None:
            iptables_cmd = "sudo iptables"
        if isc_dhcp_server_cmd is None:
            isc_dhcp_server_cmd = "sudo /etc/init.d/isc-dhcp-server"
        if tiny_proxy_cmd is None:
            tiny_proxy_cmd = "sudo /etc/init.d/tinyproxy"
        if tftpd_hpa_cmd is None:
            tftpd_hpa_cmd = "sudo /etc/init.d/tftpd-hpa"
        if reboot_cmd is None:
            reboot_cmd = "sudo reboot"
        if killall_cmd is None:
            killall_cmd = "sudo killall"
        if sysctl_cmd is None:
            sysctl_cmd = "sudo sysctl"
        if delete_dhcp_client_leases_cmd is None:
            delete_dhcp_client_leases_cmd = "sudo /usr/bin/delete_dhcp_leases"
            #delete_dhcp_client_leases_cmd = "rm /var/lib/dhcp/dhclient.leases"
        if write_to_dhcpd is None:
            write_to_dhcpd = "sudo /usr/bin/write_to_dhcpd"
            #write_to_dhcpd = "cat > /etc/dhcp/dhcpd.conf"

        pexpect.spawn.__init__(self,
                               command="ssh",
                               args=['%s@%s' % (username, name),
                                     '-p', port,
                                     '-o', 'StrictHostKeyChecking=no',
                                     '-o', 'UserKnownHostsFile=/dev/null'])
        self.name = name
        self.color = color
        self.output = output
        self.username = username
        self.password = password
        self.port = port
        self.location = location

        self.ifconfig_cmd = ifconfig_cmd
        self.aptget_cmd = aptget_cmd
        self.route_cmd = route_cmd
        self.dhclient_cmd = dhclient_cmd
        self.ip_cmd = ip_cmd
        self.iptables_cmd = iptables_cmd
        self.isc_dhcp_server_cmd = isc_dhcp_server_cmd
        self.tiny_proxy_cmd = tiny_proxy_cmd
        self.tftpd_hpa_cmd = tftpd_hpa_cmd
        self.reboot_cmd = reboot_cmd
        self.killall_cmd = killall_cmd
        self.sysctl_cmd = sysctl_cmd
        self.delete_dhcp_client_leases_cmd = delete_dhcp_client_leases_cmd
        self.write_to_dhcpd = write_to_dhcpd

        cprint("%s device console = %s" % (name, colored(color, color)), None, attrs=['bold'])
        try:
            i = self.expect(["yes/no", "assword:", "Last login"], timeout=30)
        except pexpect.TIMEOUT as e:
            raise Exception("Unable to connect to %s." % name)
        except pexpect.EOF as e:
            if hasattr(self, "before"):
                print(self.before)
            raise Exception("Unable to connect to %s." % name)
        if i == 0:
            self.sendline("yes")
            i = self.expect(["Last login", "assword:"])
        if i == 1:
            self.sendline(password)
        else:
            pass
        self.expect(self.prompt)

        if reboot:
            self.reset()

        self.logfile_read = output

    def reset(self):
        self.run_reboot()
        self.expect(['going down','disconnected'])
        try:
            self.expect(self.prompt, timeout=10)
        except:
            pass
        time.sleep(15)  # Wait for the network to go down.
        for i in range(0, 20):
            try:
                pexpect.spawn('ping -w 1 -c 1 ' + self.name).expect('64 bytes', timeout=1)
            except:
                print(self.name + " not up yet, after %s seconds." % (i + 15))
            else:
                print("%s is back after %s seconds, waiting for network daemons to spawn." % (self.name, i + 14))
                time.sleep(15)
                break
        self.__init__(self.name, self.color,
                      self.output, self.username,
                      self.password, self.port,
                      reboot=False)

    def get_ip_addr(self, interface):
        self.run_ifconfig(interface)
        self.expect('addr:(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}).*(Bcast|P-t-P):', timeout=5)
        ipaddr = self.match.group(1)
        self.expect(self.prompt)
        return ipaddr

    def ip_neigh_flush(self):
        self.run_ip('-s neigh flush all')
        self.expect('flush all')
        self.expect(self.prompt)

    def turn_on_pppoe(self):
        self.run_aptget('-o Dpkg::Options::="--force-confnew" -y install pppoe')
        self.expect(self.prompt)
        self.sendline('cat > /etc/ppp/pppoe-server-options << EOF')
        self.sendline('noauth')
        self.sendline('ms-dns 8.8.8.8')
        self.sendline('ms-dns 8.8.4.4')
        self.sendline('EOF')
        self.expect(self.prompt)
        self.sendline('pppoe-server -k -I eth1 -L 192.168.2.1 -R 192.168.2.10 -N 4')
        self.expect(self.prompt)

    def turn_off_pppoe(self):
        self.sendline("\n")
        self.run_killall("pppoe-server pppoe pppd")
        self.expect("pppd")
        self.expect(self.prompt)

    def restart_tftp_server(self):
        self.sendline('\n')
        self.run_tftpd_hpa('restart')
        self.expect('Restarting')
        self.expect(self.prompt)

    def configure(self, kind):
        if kind == "wan_device":
            self.setup_as_wan_gateway()
        elif kind == "lan_device":
            self.setup_as_lan_device()

    def setup_as_wan_gateway(self):
        self.run_killall('iperf ab hping3')
        self.expect(self.prompt)
        self.sendline('\n')
        self.run_sysctl('net.ipv6.conf.all.disable_ipv6=0')
        self.expect('sysctl ')
        self.expect(self.prompt)

        # potential cleanup so this wan device works
        self.run_iptables('-t nat -X')
        self.expect(self.prompt)
        self.run_iptables('-t nat -F')
        self.expect(self.prompt)

        # install packages required
        self.run_aptget('-o DPkg::Options::="--force-confnew" -qy install tftpd-hpa isc-dhcp-server procps iptables lighttpd')
        self.expect(self.prompt)

        # set WAN ip address
        self.run_ifconfig('eth1 192.168.0.1')
        self.expect(self.prompt)

        # configure DHCP server
        '''
        self.run_isc_dhcp_server('stop');
        self.expect(self.prompt)
        self.sendline('sed s/INTERFACES=.*/INTERFACES=\\"eth1\\"/g -i /etc/default/isc-dhcp-server')
        self.expect(self.prompt)
        self.write_to_dhcpd('<< EOF')
        self.sendline('ddns-update-style none;')
        self.sendline('option domain-name "bigfoot-test";')
        if self.location == "chennai":
            self.sendline('option domain-name-servers 10.12.0.151, 10.12.0.150, 129.46.132.7;')
        else:
            self.sendline('option domain-name-servers 10.222.148.20, 10.43.5.77, 10.43.6.93;')
        self.sendline('default-lease-time 600;')
        self.sendline('max-lease-time 7200;')
        self.sendline('subnet 192.168.0.0 netmask 255.255.255.0 {')
        self.sendline('          range 192.168.0.10 192.168.0.100;')
        self.sendline('          option routers 192.168.0.1;')
        self.sendline('}')
        self.sendline('EOF')
        self.expect(self.prompt)
        self.run_isc_dhcp_server("start");
        self.expect(['Starting ISC DHCP server.*dhcpd.', 'Starting isc-dhcp-server.*'])
        self.expect(self.prompt)
'''
        # configure routing
        self.run_sysctl('net.ipv4.ip_forward=1')
        self.expect(self.prompt)
        wan_ip_uplink = self.get_ip_addr("eth0")
        self.run_iptables('-t nat -A POSTROUTING -o eth0 -j SNAT --to-source %s' % wan_ip_uplink)
        self.expect(self.prompt)

        #configure tftp server
        '''
        self.run_tftpd_hpa('stop')
        self.expect('Stopping')
        self.expect(self.prompt)
        self.sendline('rm -rf /tftpboot')
        self.expect(self.prompt)
        self.sendline('rm -rf /srv/tftp')
        self.expect(self.prompt)
        self.sendline('mkdir -p /srv/tftp')
        self.expect(self.prompt)
        self.sendline('ln -sf /srv/tftp/ /tftpboot')
        self.expect(self.prompt)
        self.sendline('mkdir -p /tftpboot/tmp')
        self.expect(self.prompt)
        self.sendline('mkdir -p /tftpboot/crashdump')
        self.expect(self.prompt)
        self.sendline('chmod a+w /tftpboot/crashdump')
        self.expect(self.prompt)
        self.sendline('sed /TFTP_OPTIONS/d -i /etc/default/tftpd-hpa')
        self.expect(self.prompt)
        self.sendline('echo TFTP_OPTIONS=\\"-4 --secure --create\\" >> /etc/default/tftpd-hpa')
        self.expect(self.prompt)
        self.sendline('sed /TFTP_DIRECTORY/d -i /etc/default/tftpd-hpa')
        self.expect(self.prompt)
        self.sendline('echo TFTP_DIRECTORY=\\"/srv/tftp\\" >> /etc/default/tftpd-hpa')
        self.expect(self.prompt)
        self.run_tftpd_hpa('restart')
        self.expect(self.prompt)
        '''

        self.run_sysctl('net.ipv4.tcp_timestamps=0')
        self.expect(self.prompt)
        self.run_sysctl('net.ipv4.tcp_sack=0')
        self.expect(self.prompt)

        self.run_ifconfig('eth1')
        self.expect(self.prompt)

        self.turn_off_pppoe()

    def setup_as_lan_device(self):
        # potential cleanup so this wan device works
        self.killall_cmd('iperf ab hping3')
        self.expect(self.prompt)
        self.sendline("\n")
        self.run_iptables('-t nat -X')
        self.expect('iptables -t')
        self.expect(self.prompt)
        self.run_sysctl('net.ipv6.conf.all.disable_ipv6=0')
        self.expect(self.prompt)
        self.run_sysctl('net.ipv4.ip_forward=1')
        self.expect(self.prompt)
        self.run_iptables('-t nat -F')
        self.run_iptables('-t nat -X')
        self.expect(self.prompt)
        self.run_iptables('-F')
        self.run_iptables('-X')
        self.expect(self.prompt)
        self.run_iptables('-t nat -A PREROUTING -p tcp --dport 222 -j DNAT --to-destination 192.168.1.1:22')
        self.expect(self.prompt)
        self.run_iptables('-t nat -A POSTROUTING -o eth1 -p tcp --dport 22 -j MASQUERADE')
        self.expect(self.prompt)
        self.run_sysctl('net.ipv4.tcp_timestamps=0')
        self.expect(self.prompt)
        self.run_sysctl('net.ipv4.tcp_sack=0')
        self.expect(self.prompt)
        self.killall_cmd('dhclient')
        self.expect(self.prompt)

    def start_lan_client(self):
        self.ifconfig_cmd('eth1 0.0.0.0')
        self.expect('ifconfig eth1')
        self.expect(self.prompt)
        self.run_delete_dhcp_client_leases()
        self.expect(self.prompt)
        for attempt in range(3):
            try:
                self.run_dhclient('-v eth1')
                self.expect('DHCPOFFER', timeout=30)
                self.expect(self.prompt)
                break
            except:
                self.sendcontrol('c')
        else:
            raise Exception("Error: Device on LAN couldn't obtain address via DHCP.")
        self.run_ifconfig('eth1')
        self.expect(self.prompt)
        self.run_route('del default')
        self.expect(self.prompt)
        self.run_route('del default')
        self.expect(self.prompt)
        self.run_route('del default')
        self.expect(self.prompt)
        self.run_route('add default gw 192.168.1.1')
        self.expect(self.prompt)
        # Setup HTTP proxy, so board webserver is accessible via this device
        self.run_aptget('-qy install tinyproxy curl apache2-utils nmap')
        self.expect('Reading package')
        self.expect(self.prompt, timeout=150)
        self.sendline('curl --version')
        self.expect(self.prompt)
        self.sendline('ab -V')
        self.expect(self.prompt)
        self.sendline('nmap --version')
        self.expect(self.prompt)
        self.sendline("sed -i 's/^Port 8888/Port 8080/' /etc/tinyproxy.conf")
        self.expect(self.prompt)
        self.sendline("sed -i 's/^#Allow 10.0.0.0/Allow 10.0.0.0/' /etc/tinyproxy.conf")
        self.expect(self.prompt)
        self.run_tiny_proxy("restart")
        self.expect('Restarting')
        self.expect(self.prompt)
        # Write a useful ssh config for routers
        self.sendline('mkdir -p ~/.ssh')
        self.sendline('cat > ~/.ssh/config << EOF')
        self.sendline('Host 192.168.1.1')
        self.sendline('StrictHostKeyChecking no')
        self.sendline('UserKnownHostsFile=/dev/null')
        self.sendline('')
        self.sendline('Host krouter')
        self.sendline('Hostname 192.168.1.1')
        self.sendline('StrictHostKeyChecking no')
        self.sendline('UserKnownHostsFile=/dev/null')
        self.sendline('EOF')
        self.expect(self.prompt)
        # Copy an id to the router so people don't have to type a password to ssh or scp
        self.sendline('[ -e /root/.ssh/id_rsa ] || ssh-keygen -N "" -f /root/.ssh/id_rsa')
        self.expect(self.prompt)
        self.sendline('scp ~/.ssh/id_rsa.pub 192.168.1.1:/etc/dropbear/authorized_keys')
        try:
            # When resetting, no need for password
            self.expect("root@192.168.1.1's password:", timeout=5)
            self.sendline('password')
        except:
            pass
        self.expect(self.prompt)



    def send_sudo(self, command):
        self.sendline("sudo %s" % command)

    def run_ifconfig(self, command):
        self.sendline("\n%s %s" % (self.ifconfig_cmd, command))

    def run_aptget(self, command):
        self.sendline('%s %s' % (self.aptget_cmd, command))

    def run_route(self, command):
        self.sendline('%s %s' % (self.route_cmd, command))

    def run_dhclient(self, command):
        self.sendline('%s %s' % (self.dhclient_cmd, command))

    def run_ip(self, command):
        self.sendline('%s %s' % (self.ip_cmd, command))

    def run_iptables(self, command):
        self.sendline('%s %s' % (self.iptables_cmd, command))

    def run_isc_dhcp_server(self, command):
        self.sendline('%s %s' % (self.isc_dhcp_server_cmd, command))

    def run_tiny_proxy(self, command):
        self.sendline('%s %s' % (self.tiny_proxy_cmd, command))

    def run_tftpd_hpa(self, command):
        self.sendline('%s %s' % (self.tftpd_hpa_cmd, command))

    def run_reboot(self):
        self.sendline(self.reboot_cmd)

    def run_killall(self, command):
        self.sendline('%s %s' % (self.killall_cmd, command))

    def run_sysctl(self, command):
        self.sendline('%s %s' % (self.sysctl_cmd, command))

    def run_delete_dhcp_client_leases(self, command):
        self.sendline(self.delete_dhcp_client_leases_cmd)

    def run_write_to_dhcpd(self, command):
        self.sendline('%s %s' % (self.write_to_dhcpd, command))
if __name__ == '__main__':
    # Example use
    dev = DebianBox('10.0.0.173',
                    'blue')
    dev.sendline('echo Hello')
    dev.expect('Hello', timeout=4)
    dev.expect(dev.prompt)
    dev.reset()
    dev.sendline('echo Hello')
    dev.expect('Hello', timeout=4)
    dev.expect(dev.prompt)
