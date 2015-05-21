#!/usr/bin/python
from bar import Bar
import time
# from mpd import MPDClient, ConnectionError
import os
import widgets

PID_FILE = '/home/ellis/.bar_pid'

if __name__ == '__main__':
    bar = Bar()
    bar.foreground = 'white'
    bar.height = '20'
    bar.font = ['stlarch:size=8', 'ohsnap.icons:size=8']
    bar.start()

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
        f.write('\n')
        f.write(str(bar.get_pid()))

    mpdwidget = widgets.MpdWidget(bar=bar, position='right')
    mpdwidget.background = 'dark_green'
    mpdwidget.icon = ''

    wifiwidget = widgets.WiFiWidget(bar=bar, position='right')
    wifiwidget.background = 'magenta'
    wifiwidget.icon = ''

    batterywidget = widgets.BatteryWidget(bar=bar, position='right')
    batterywidget.icon = ''
    batterywidget.hide_value = 100
    batterywidget.background = 'blue'

    clockwidget = widgets.ClockWidget(bar=bar, position='right')
    clockwidget.background = 'red'
    clockwidget.icon = ''

    workspacewidget = widgets.BSPWMWorkspaceWidget(
        labels=[i for i in '¹rchlinux'],
        bar=bar, position='left')
    workspacewidget.background = 'dark_blue'

    while 1:
        time.sleep(30)
