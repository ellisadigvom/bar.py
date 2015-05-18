#!/usr/bin/python
from bar import Bar
import time
#from mpd import MPDClient, ConnectionError
from subprocess import getoutput
import re
import os
import widgets

PID_FILE = '/home/ellis/.bar_pid'

if __name__ == '__main__':
    bar = Bar()
    bar.foreground = 'white'
    bar.height = '20'
    bar.font = 'ohsnap.icons:size=8'
    bar.start()

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
        f.write('\n')
        f.write(str(bar.get_pid()))

    mpdwidget = widgets.MpdWidget(bar=bar, position='right', icon=None)
    mpdwidget.background = 'dark_green'
    # mpdwidget.foreground = 'white'

    wifiwidget = widgets.WiFiWidget(bar=bar, position='right', icon=None)
    wifiwidget.background = 'magenta'
    # ifiwidget.foreground = 'white'

    batterywidget = widgets.BatteryWidget(bar=bar, position='right', icon=None)
    batterywidget.background = 'blue'
    # batterywidget.foreground = 'white'

    clockwidget = widgets.ClockWidget(bar=bar, position='right', icon=None)
    clockwidget.background = 'red'
    # clockwidget.foreground = 'white'

    # taskbarwidget = widgets.TaskbarWidget(bar=bar, position='center', icon=None)
    # titlewidget = widgets.TitleWidget(bar=bar, position='left')

    workspacewidget = widgets.BSPWMWorkspaceWidget(labels=[i for i in '¹archlinux'],
            bar=bar, position='left')
    workspacewidget.background = 'dark_blue'
    # workspacewidget.foreground = 'white'



    while 1:
        time.sleep(30)
