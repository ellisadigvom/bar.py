from time import strftime, sleep
import subprocess
import re
from itertools import zip_longest
import threading
import shlex

#TODO: Clean up init methods
class Widget(threading.Thread):
    def __init__(self, bar, position='center', icon=None):
        if not bar:
            raise ValueError
        self._bar = bar
        self._icon = icon
        self.text = ''
        bar.register(self, position=position)
        self.format_icon()
        super().__init__()
        self.start()

    def update(self, text):
        self.text = text
        if text:
            self.iconify()
        self._bar.redraw()

    def format_icon(self):
        # Color the icon and whatever at widget init
        if self._icon:
            pass

    def _update_icon(self, icon):
        pass

    def iconify(self):
        if self._icon:
            self.text = '{}{}{}'.format(self._icon,
                self._bar.resources['icon_separator'], self.text)

class SkeletonWidget(Widget):
    def __init__(self, icon=None, **kwargs):
        # Do init stuff here
        super().__init__(icon=icon, **kwargs)

    def run(self):
        text = 'Stuff you want to display'
        self.update(text)

class StaticTextWidget():
    def __init__(self, text):
        self._text = text

class ClockWidget(Widget):
    def __init__(self, format='%a %d %b %H:%M', icon='È', **kwargs):
        self._format = format
        super().__init__(icon=icon, **kwargs)

    def run(self):
        while 1:
            print('clock')
            self.update(strftime(self._format))
            seconds = int(strftime('%S'))
            sleep(60 - seconds)

#TODO: Implement the clicky widget
# a.k.a the button widget
class ClickyWidget(Widget):
    def __init__(self):
        pass

class BSPWMWorkspaceWidget(Widget):
    def __init__(self, labels=[], **kwargs):
        self._labels = labels
        super().__init__(**kwargs)

    def run(self):
        bspc_subscribe = subprocess.Popen (['bspc', 'control', '--subscribe'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        while 1:
            print('workspace')
            text = ''
            line = bspc_subscribe.stdout.readline()
            workspaces = line.split(':')[1:-1]
            for workspace, label in zip_longest(workspaces, self._labels):
                active = False
                occupied = False

                if workspace[0].isupper():
                    active = True
                if workspace[0].lower() == 'o':
                    occupied = True

                if label:
                    workspace_text = ' {} '.format(label)
                else:
                    workspace_text = ' {} '.format(workspace[1:])
                if active:
                    workspace_text = self._bar.format(workspace_text, invert=True)
                if occupied:
                    workspace_text = self._bar.format(workspace_text, underline=True)
                text += workspace_text

            self.update(text)

class MpdWidget(Widget):
    def __init__(self, icon='ê', host='localhost', port='6600', **kwargs):
        self._host=host
        self._port=port
        super().__init__(icon=icon, **kwargs)

    def _get_data(self):
        title = None
        artist = None
        playing = False
        mpc_output = subprocess.getoutput('mpc status --format {} -h {} -p {}'.format(
            '%title%---%artist%', self._host, self._port))
        lines = mpc_output.splitlines()

        # Is it stopped?
        if len(lines) == 1:
            return {'title': '', 'artist': '', 'playing': False, 'pos': 0}

        # Title and artist
        match = re.match('^(.*)---(.*)$', lines[0])
        if match:
            title = match.group(1)
            artist = match.group(2)

        # Playing or paused
        match = re.match('\[(.+)\]', lines[1])
        if match:
            if match.group(1) == 'playing':
                playing = True
            elif match.group(1) == 'paused':
                playing = False

        # Position, length
        match = re.search(' (\d+)\:(\d+)/(\d+)\:(\d+) ', lines[1])
        now_min, now_sec, len_min, len_sec = [int(i) for i in match.groups()]
        position = (now_min * 60) + now_sec
        length = (len_min * 60) + len_sec

        return {'title': title, 'artist': artist, 'playing': playing,
                'position': position, 'length': length}

    def run(self):
        while 1:
            print('mpd')
            time_to_next_update = None
            data = self._get_data()
            if data['playing']:
                text = '{} - {}'.format(data['title'], data['artist'])

                # Drawing the underline progress bar
                text_length = len(text)
                position = int(text_length * (data['position'] / data['length']))
                text = self._bar.format(text[:position], underline=True) \
                    + text[position:]
            
                time_to_next_update = float(data['length'] / text_length)
                self.update(text)
            else:
                self.update(None)

            process = subprocess.Popen(shlex.split('mpc -h {} -p {} idle player'
                .format(self._host, self._port)))#, stdout=subprocess.PIPE)
            try:
                process.wait(time_to_next_update)
            except subprocess.TimeoutExpired:
                process.kill()

class BatteryWidget(Widget):
    def __init__(self, icon='ó', hide_value=80, **kwargs):
        self._hide_value = hide_value
        super().__init__(icon=icon, **kwargs)

    def _get_percentage(self):
        charge_full = int(open('/sys/class/power_supply/BAT1/charge_full').read())
        charge_now = int(open('/sys/class/power_supply/BAT1/charge_now').read())
        charge_percentage = (charge_now / charge_full) * 100
        return int(charge_percentage)

    def run(self):
        print('bat')
        while 1:
            percentage = self._get_percentage()
            if percentage > self._hide_value:
                self.update(None)
            else:
                self.update(str(percentage))
            sleep(30)

class WiFiWidget(Widget):
    def __init__(self, icon='¤', adapter='wlp2s0', **kwargs):
        self._adapter = adapter
        super().__init__(icon=icon, **kwargs)

    def _get_essid(self):
        print('wifi')
        data = subprocess.getoutput('iwconfig ' + self._adapter)
        match = re.search('ESSID:"(.*)"', data)
        if match:
            return match.group(1).strip()
        else:
            return None

    def run(self):
        while 1:
            essid = self._get_essid()
            if not essid:
                self.update('')
            else:
                self.update(essid)
            sleep(5)
