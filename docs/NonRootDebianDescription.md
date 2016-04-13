For maintainability and security, it's ideal that one would not need to connect to and run tests on LAN and WAN devices as root. This pull request makes the changes necessary to allow this use-case without interfering with those who run WAN and LAN as root. I'll attempt to summarize the mechanism used.

This pull requests implements this by adding the following files:

* **devices/local_debian_setup.py**: tool for running the functions in devices/debian.py on the local computer, not a remote computer like in
DebianBox
* **devices/non_root_debian.py**: an alternative to DebianBox which supports running the commands in DebianBox while connecting to LAN/WAN computer as a non-root user.
* **devices/debian_decider.py**: contains a function for deciding whether to initialize and return DebianBox or NonRootDebianBox based upon the username provided in the config. (If 'root', use DebianBox, otherwise use NonRootDebianBox).

# How does this all work?
In general, the functions which require root access in DebianBox are in NonRootDebianBox wrapped to be called through LocalDebianSetup.

Let's look at how DebianBox and NonRootDebianBox handle a simple function like `restart_tftp_server`.

In DebianBox, `restart_tftp_server` is as follows:
```python
def restart_tftp_server(self):
    self.sendline('\n/etc/init.d/tftpd-hpa restart')
    self.expect('Restarting')
    self.expect(self.prompt)
```
To understand, the controller (the computer running BFT), sends `/etc/init.d/tftpd-hpa restart` to the Debian computer via their SSH connection and then waits for a response.

In NonRootDebianBox this is handled quite differently:
```python
def restart_tftp_server(self):
    self.sendline('\nsudo restart_tftp_server')
    self.expect('Restarting')
    self.expect(self.prompt)
```
In this case, we're calling a shell script on the WAN computer named restart_tftp_server via sudo. The restart_tftp_server script isn't included but mine looks like so:
```shell

```

# Additional setup necessary on the LAN and WAN computers
Add

# Important note
This change should not
