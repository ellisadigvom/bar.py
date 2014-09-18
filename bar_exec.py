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
    bar.start()
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
        f.write('\n')
        f.write(str(bar.get_pid()))

    mpdwidget = widgets.MpdWidget(icon='ê')
    clockwidget = widgets.ClockWidget(icon='È')
    wifiwidget = widgets.WiFiWidget(icon='¤')
    batterywidget = widgets.BatteryWidget(icon='ó')
    archwidget = widgets.StaticTextWidget(text='arch')
    workspacewidget = widgets.WorkspaceWidget(
            workspace_labels=[' ' + i + ' ' for i in 'archlinux'],
            active_fg = '#ff1f1f1f',
            active_bg = '#ff856162',
            workspace_separator='')

    while 1:
        left = [workspacewidget]
        center = []
        right=[mpdwidget, wifiwidget,
               batterywidget, clockwidget]
        bar.draw_widgets(left, center, right)
        time.sleep(.3)
