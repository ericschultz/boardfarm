import base
import pexpect
import debian
import sys
import argparse
from termcolor import colored, cprint

class LocalDebianSetup(debian.DebianBox):
    prompt = ['root\\@.*:.*#', '/ # ', ".*:~ #", ".*:~.*\\$", ".*\\@.*:.*\\$" ]

    def __init__(self,
                 color,
                 output=sys.stdout,
                 reboot=False,
                 location=None
                 ):

        pexpect.spawn.__init__(self,
                               command="bash")

        self.color = color
        self.output = output
        self.location = location
        self.sendline("set -x")
        cprint("%s device console = %s" % ("local device", colored(color, color)), None, attrs=['bold'])
        self.expect(self.prompt)

        if reboot:
            self.reset()

        self.logfile_read = output

    def setup_as_wan_gateway(self):
        debian.DebianBox.setup_as_wan_gateway(self)
    def setup_as_lan_device(self):
        debian.DebianBox.setup_as_lan_device(self)
    def start_lan_client(self):
        debian.DebianBox.start_lan_client(self)

    def restart_tftp_server(self):
        debian.DebianBox.restart_tftp_server(self)

    def turn_on_pppoe(self):
        debian.DebianBox.turn_on_pppoe(self)
    def ip_neigh_flush(self):
        debian.DebianBox.ip_neigh_flush(self)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=['init_wan', 'init_lan', 'start_lan_client', 'restart_tftp_server', 'turn_on_pppoe', 'ip_neigh_flush'])


    args = parser.parse_args()
    dev = LocalDebianSetup('blue')


    if args.action == "init_wan":
        dev.setup_as_wan_gateway()
    elif args.action == 'init_lan':
        dev.setup_as_lan_device()
    elif args.action == 'start_lan_client':
        dev.start_lan_client()
    elif args.action == 'restart_tftp_server':
        dev.restart_tftp_server()
    elif args.action == 'ip_neigh_flush':
        dev.ip_neigh_flush()
    elif args.action == 'turn_on_pppoe':
        dev.turn_on_pppoe()
    else:
        parser.print_help()
