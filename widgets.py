# coding: utf-8

from time import strftime, sleep
import subprocess
import re
from itertools import zip_longest
import threading
import shlex
from os import path


# TODO: Clean up init methods
# FIXME: Widgets start to execute as soon as they are created. They shouldn't
class Widget(threading.Thread):
    def __init__(self, bar, position='center'):
        if not bar:
            raise ValueError
        self._bar = bar
        self.icon = None
        self.background = 'background'
        self.foreground = 'foreground'
        self.line_color = self.foreground
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
        if self.icon:
            pass

    def _update_icon(self, icon):
        pass

    def format(self, text, **kwargs):
        return self._bar.format(text, **kwargs)

    def iconify(self):
        if self.icon:
            self.text = '{} {}'.format(self.icon, self.text)

    def make_clickable(self, text, args, button=''):
        return self._bar.make_clickable(text, args, self, button)


    def click_handler(self, args):
        """ Handle click events
        """
        pass


class SkeletonWidget(Widget):
    def __init__(self, **kwargs):
        # Do init stuff here
        super().__init__(**kwargs)

    def click_handler(self, args):
        """ Handle click events
        """
        pass

    def run(self):
        text = 'Stuff you want to display'
        self.update(text)


class StaticTextWidget():
    def __init__(self, text):
        self._text = text


class ClockWidget(Widget):
    def __init__(self, **kwargs):
        self.format_string = '%a %d %b %H:%M'
        super().__init__(**kwargs)

    def run(self):
        while 1:
            self.update(strftime(self.format_string))
            seconds = int(strftime('%S'))
            sleep(60 - seconds)


# TODO: Implement the clicky widget
# a.k.a the button widget
class ClickyWidget(Widget):
    def __init__(self):
        pass


class BSPWMWorkspaceWidget(Widget):
    def __init__(self, labels=None, **kwargs):
        if not labels:
            labels = []
        self._labels = labels
        super().__init__(**kwargs)

    def run(self):
        bspc_subscribe = subprocess.Popen(
            ['bspc', 'control', '--subscribe'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True)

        while 1:
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
                    workspace_text = self.format(workspace_text, invert=True)
                if occupied:
                    workspace_text = self.format(workspace_text,
                                                 underline=True)
                workspace_text = self.make_clickable(
                    workspace_text,
                    'switch-to {}'.format(workspace[1:]))
                text += workspace_text

            self.update(text)

    def click_handler(self, arguments):
        subprocess.call(['bspc', 'desktop', '-f', arguments[1]])


# FIXME: Bad things happen when mpd is not running
# TODO: Use a python mpd library
class MpdWidget(Widget):
    def __init__(self, host='localhost', port='6600', **kwargs):
        self._host = host
        self._port = port
        super().__init__(**kwargs)

    def _get_data(self):
        title = None
        artist = None
        playing = False
        mpc_output = subprocess.getoutput(
            'mpc status --format {} -h {} -p {}'.format(
                '%title%---%artist%---%file%', self._host, self._port))
        lines = mpc_output.splitlines()

        # Is it stopped?
        if len(lines) == 1:
            return {'title': '', 'artist': '', 'playing': False, 'pos': 0}

        # Title and artist
        match = re.match('^(.*)---(.*)---(.*)$', lines[0])
        if match:
            title = match.group(1)
            artist = match.group(2)
            filename = match.group(3)

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
                'position': position, 'length': length, 'filename': filename}

    def run(self):
        while 1:
            # Dirty fix for when mpd is not running
            try:
                time_to_next_update = None
                data = self._get_data()
                if data['playing']:
                    if not (data['title']):
                        text = '{}'.format('.'.join(path.basename(data['filename']).split('.')[:-1]))
                    else:
                        text = '{} - {}'.format(data['title'], data['artist'])

                    # Drawing the underline progress bar
                    text_length = len(text)
                    position = int(text_length * (data['position'] / data['length']))
                    text = self.format(text[:position], underline=True) \
                        + text[position:]

                    time_to_next_update = float(data['length'] / text_length)
                    self.update(text)
                else:
                    self.update(None)

                process = subprocess.Popen(shlex.split('mpc -h {} -p {} idle player'
                                                       .format(self._host, self._port)))
                try:
                    process.wait(time_to_next_update)
                except subprocess.TimeoutExpired:
                    process.kill()
            except: # Bite me
                sleep(2)



class BatteryWidget(Widget):
    def __init__(self, **kwargs):
        self.hide_value = 70
        super().__init__(**kwargs)

    def _get_percentage(self):
        charge_full = int(open('/sys/class/power_supply/BAT0/charge_full').read())
        charge_now = int(open('/sys/class/power_supply/BAT0/charge_now').read())
        charge_percentage = (charge_now / charge_full) * 100
        return int(charge_percentage)

    def run(self):
        while 1:
            percentage = self._get_percentage()
            if percentage > self.hide_value:
                self.update(None)
            else:
                self.update(str(percentage))
            sleep(30)


class WiFiWidget(Widget):
    def __init__(self, adapter='wlp7s0', **kwargs):
        self._adapter = adapter
        super().__init__(**kwargs)

    def _get_essid(self):
        data = subprocess.getoutput('iwconfig ' + self._adapter)
        match = re.search('ESSID:"(.*)"', data)
        if match:
            return match.group(1).strip()
        else:
            return None

    def run(self):
        while 1:
            text = ''
            essid = self._get_essid()
            if essid:
                text = essid
            else:
                text = ''
                self.update(text)
                sleep(5)
                next

            data = subprocess.getoutput('ip addr').splitlines()
            interface_data = {}
            current_interface = ''
            for line in data:
                match = re.match('\d: (.+):', line)
                if match:
                    current_interface = match.group(1)
                    interface_data[current_interface] = [line]
                else:
                    interface_data[current_interface].append(line)
            for line in interface_data[self._adapter]:
                match = re.match('\s+inet (\d+\.\d+.\d+.\d+)', line)
                if match:
                    ip = match.group(1)
                    text = '{} {}'.format(text, ip)
                    break
            self.update(text)
            sleep(5)

#TODO: Finish the taskbar widget
class TaskbarWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def click_handler(self, args):
        """ Handle click events
        """
        subprocess.getoutput('bspc window -f {}'.format(args[0]))

    def run(self):
        bspc_subscribe = subprocess.Popen(['bspc', 'control', '--subscribe'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        while 1:
            windows = subprocess.getoutput('bspc query -W -d focused').splitlines()
            data = subprocess.getoutput('bspc query --tree').splitlines()
            data = [i.strip() for i in data]
            text = ''
            for line in data:
                for window in windows:
                    if re.search(window, line):
                        match = re.match('\s*. (\S+) .+?(\*)?$', line)
                        window_name = ' {} '.format(match.group(1))
                        if match.group(2):
                            window_name = self.format(window_name, invert=True)
                        window_name = self.make_clickable(window_name, window)
                        text += window_name
            self.update(text)
            #bspc_subscribe.stdout.readline() # FIXME: Something wicked going on here
            sleep(1)

class IPAddrWidget(Widget):
    def __init__(self, interface='wlp2s0', **kwargs):
        self._interface = interface
        super().__init__(**kwargs)

    def click_handler(self, args):
        """ Handle click events
        """
        pass

    def run(self):
        while 1:
            data = subprocess.getoutput('ip addr').splitlines()
            interface_data = {}
            current_interface = ''
            for line in data:
                match = re.match('\d: (.+):', line)
                if match:
                    current_interface = match.group(1)
                    interface_data[current_interface] = [line]
                else:
                    interface_data[current_interface].append(line)
            for line in interface_data[self._interface]:
                match = re.match('\s+inet (\d+\.\d+.\d+.\d+)', line)
                if match:
                    ip = match.group(1)
                    self.update(ip)
                    break
                else:
                    self.update('')
            sleep(10)

class TitleWidget(Widget):
    def __init__(self, **kwargs):
        # Do init stuff here
        super().__init__(**kwargs)

    def click_handler(self, args):
        """ Handle click events
        """
        pass

    def run(self):
        xtitle = subprocess.Popen(['xtitle', '-s'], stdout=subprocess.PIPE, universal_newlines=True)
        while 1:
            self.update(xtitle.stdout.readline().strip())
