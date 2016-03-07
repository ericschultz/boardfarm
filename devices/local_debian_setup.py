import base
import pexpect
import debian
import sys
import argparse
from termcolor import colored, cprint

class LocalDebianSetup(base.BaseDevice):
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("box_action", choices=['init_wan', 'init_lan', 'start_lan_client'])


    args = parser.parse_args()
    dev = LocalDebianSetup('blue')


    if args.action == "init_wan":
        dev.setup_as_wan_gateway()
    elif args.action == 'init_lan':
        dev.setup_as_lan_device()
    elif args.action == 'start_lan_client':
        dev.start_lan_client()
    else:
        parser.print_help()
