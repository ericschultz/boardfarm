# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import common
import openwrt_router

class LantiqRouter(openwrt_router.OpenWrtRouter):
    '''
    Lantiq Router support
    '''

    prompt = ['root\\@.*:.*#', ]
    uprompt = ['VR9 #']

    def __init__(self, *args, **kwargs):
        super(LantiqRouter, self).__init__(*args, **kwargs)

    def flash_meta(self, META_BUILD):
        common.print_bold("\n===== Flashing image on=====\n")
        file = self.prepare_file(META_BUILD)
        self.sendline('run update_fullimage')
        self.expect(self.uprompt, timeout=60)
        self.reset()
        self.wait_for_boot()

    def boot_linux(self, rootfs=None):
        self.sendline("run bootcmd")
