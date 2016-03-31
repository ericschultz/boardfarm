import debian
import non_root_debian
import sys

def debian(name, color,
                    username,
                    password,
                    port,
                    output=sys.stdout,
                    reboot=False,
                    location=None):
    if (username is 'root'):
        return debian.DebianBox(name=name, color=color, username=username,
                                password=password, port=port, output=output,
                                reboot=reboot, location=location)
    else:
        return non_root_debian.NonRootDebianBox(name=name, color=color, username=username,
                                                password=password, port=port, output=output,
                                                reboot=reboot, location=location)
