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
import argparse

from termcolor import colored, cprint


class NonRootDebianBox(base.BaseDevice):
    '''
    A linux machine running an ssh server.
    '''

    prompt = ['root\\@.*:.*#', '/ # ', ".*:~ #", ".*:~.*\\$", ".*\\@.*:.*\\$" ]

    def __init__(self,
                 name,
                 color,
                 output=sys.stdout,
                 username=None,
                 password=None,
                 port=None,
                 reboot=False,
                 location=None
                 ):
        if name is None:
            return
        if username is None:
            username='root'
        if password is None:
            password='bigfoot1'
        if port is None:
            port='22'

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
        self.sendline("exec 2> /tmp/run.log")
        self.sendline("exec 1>&2")
        self.sendline("set -x")
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
        self.sendline('sudo reboot')
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
        self.sendline("\nifconfig %s" % interface)
        self.expect('addr:(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}).*(Bcast|P-t-P):', timeout=5)
        ipaddr = self.match.group(1)
        self.expect(self.prompt)
        return ipaddr

    def ip_neigh_flush(self):
        self.sendline('\nsudo ip_neigh_flush')
        self.expect('flush all')
        self.expect(self.prompt)

    def turn_on_pppoe(self):
        self.sendline('sudo turn_on_pppoe')
        self.expect(self.prompt)

    def turn_off_pppoe(self):
        pass

    def restart_tftp_server(self):
        self.sendline('\nsudo restart_tftp_server')
        self.expect('Restarting')
        self.expect(self.prompt)

    def configure(self, kind):
        if kind == "wan_device":
            self.setup_as_wan_gateway()
        elif kind == "lan_device":
            self.setup_as_lan_device()

    def setup_as_wan_gateway(self):
        self.sendline('\necho "needs to be setup via root. If not setup, this is bad."')

    def setup_as_lan_device(self):
        self.sendline('\necho "needs to be setup via root. If not setup, this is bad"')

    def start_lan_client(self):
        self.sendline('\nsudo start_lan_client')
        self.expect(self.prompt)
