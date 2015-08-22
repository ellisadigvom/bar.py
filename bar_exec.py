#!/usr/bin/python
# Author: Ellis Adigvom <ellisadigvom@gmail.com>
from bar import Bar
import time
import os
import widgets

PID_FILE = '/home/ellis/.bar_pid'

if __name__ == '__main__':
    bar = Bar()
    bar.foreground = 'black'
    bar.height = '25'
    bar.font = ['siji:size=8', 'ohsnap:size=8']
    bar.padding = '  '

    mpdwidget = widgets.MpdWidget()
    mpdwidget.background = 'dark_green'
    mpdwidget.icon = ''

    wifiwidget = widgets.WiFiWidget()
    wifiwidget.background = 'dark_blue'
    wifiwidget.icon = ''

    batterywidget = widgets.BatteryWidget()
    batterywidget.icon = ''
    batterywidget.hide_value = 80
    batterywidget.background = 'blue'

    clockwidget = widgets.ClockWidget()
    clockwidget.background = 'red'
    clockwidget.icon = ''

    workspacewidget = widgets.BSPWMWorkspaceWidget()
    workspacewidget.labels = [i for i in 'rchlinux']
    workspacewidget.background = 'dark_blue'

    mailwidget = widgets.MailWidget()
    mailwidget.background = 'dark_red'
    mailwidget.icon = ''

    bar.add(mpdwidget, 'r')
    bar.add(wifiwidget, 'r')
    bar.add(batterywidget, 'r')
    bar.add(mailwidget, 'r')
    bar.add(clockwidget, 'r')
    bar.add(workspacewidget, 'l')

    bar.start()

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
        f.write('\n')
        f.write(str(bar.get_pid()))

    while 1:
        time.sleep(30)
