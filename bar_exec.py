#!/usr/bin/python
from bar import Bar
import time
from mpd import MPDClient, ConnectionError
from subprocess import getoutput
import re
import os
import widgets

PID_FILE = '/home/ellis/.bar_pid'

if __name__ == '__main__':
    bar = Bar()
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
        f.write('\n')
        f.write(str(bar.get_pid()))

    clockwidget = widgets.ClockWidget(icon='È', bar=bar, position='right')
    workspacewidget = widgets.BSPWMWorkspaceWidget(labels=[i for i in'archlinux'],
            bar=bar, position='left')
    while 1:
        time.sleep(30)
