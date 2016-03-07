import base
import pexpect
import debian
import sys
import argparse

class LocalDebianSetup(base.BaseDevice):
    prompt = ['root\\@.*:.*#', '/ # ', ".*:~ #", ".*:~.*\\$", ".*\\@.*:.*\\$" ]

    def __init__(self,
                 name,
                 color,
                 output=sys.stdout,
                 reboot=False,
                 location=None
                 ):
        if name is None:
            return

        pexpect.spawn.__init__(self,
                               command="bash")
        self.name = name
        self.color = color
        self.output = output
        self.location = location
        cprint("%s device console = %s" % (name, colored(color, color)), None, attrs=['bold'])
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
    parser.add_argument("action", choices=['init_wan', 'init_lan', 'start_lan_client'])
    parser.add_argument("name", default="local_box")


    args = parser.parse_args()
    dev = LocalDebianSetup(args.name, 'blue')


    if args.action == "init_wan":
        dev.setup_as_wan_gateway()
    elif args.action == 'init_lan':
        dev.setup_as_lan_device()
    elif args.action == 'start_lan_client':
        dev.start_lan_client()
    else:
        parser.print_help()
