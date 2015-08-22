# Author: Ellis Adigvom <ellisadigvom@gmail.com>
from time import strftime, sleep
import subprocess
import re
from itertools import zip_longest
import shlex
from os import path
import requests
from requests.adapters import HTTPAdapter


class Widget():
    def __init__(self):
        # Entirely self explanatory
        self.background = 'background'
        self.foreground = 'foreground'

        # The icons are regular strings like 'a', 'b' and ''
        # I recommend the siji icon font
        self.icon = None
        self.icon_foreground = None
        self.icon_background = None

        # A list of executables that should be found in the PATH for the
        # widget to function
        self.executable_deps = []
        self._check_deps()

        # The color of the underline, if any
        self.line_color = self.foreground

        # TODO: Write methods in Bar to draw progress bars on widgets
        # This tells the Bar class to draw a progress bar under the
        # widget. It is a number from 0 to 1. If it is negative, draw
        # the bar from the right
        self.progress = 0

        # If this is a number, the Bar class waits n seconds before calling
        # update again
        # If this is a function, the Bar class calls it with no arguments and
        # waits for it to return before calling update again.
        # The return value is not used
        self.timer = 0

    def _check_deps(self):
        ''' Check for dependencies, and raise an exception if they're not found
        '''
        # TODO:
        pass

    def update(self):
        ''' Return the text to display on the bar
            This method is called in an infinite loop
        '''
        pass

    def format(self, text, **kwargs):
        return self._bar.format(text, **kwargs)

    def make_clickable(self, text, cmd, button=''):
        return self._bar.make_clickable(text, cmd, self._index, button)

    def click_handler(self, cmd):
        """ Handle click events
        """
        pass


class ClockWidget(Widget):
    def __init__(self):
        super().__init__()
        self.format_string = '%a %d %b %H:%M'
        self.first_run = True

    def update(self):
        if self.first_run:
            seconds = int(strftime('%S'))
            self.timer = seconds + 1
        else:
            self.timer = 60
        return strftime(self.format_string)

class BSPWMWorkspaceWidget(Widget):
    def __init__(self):
        super().__init__()
        self.executable_deps = ['bspc']

        self.labels = []

        self.bspc = subprocess.Popen(
            ['bspc', 'control', '--subscribe'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True)
        self.bspc_output = None

    def timer(self):
        self.bspc_output = self.bspc.stdout.readline()

    def update(self):
        if not self.bspc_output:
            self.bspc_output = subprocess.getoutput(
                'bspc control --get-status')

        text = ''
        line = self.bspc.stdout.readline()
        workspaces = line.split(':')[1:-1]
        for workspace, label in zip_longest(workspaces, self.labels):
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
                                             underline=True,
                                             line_color=self.line_color)
            # TODO: Make the workspaces clickable
            workspace_text = self.make_clickable(
                workspace_text,
                workspace[1:])
            text += workspace_text
        return text

    def click_handler(self, cmd):
        subprocess.call(['bspc', 'desktop', '-f', cmd])


class MpdWidget(Widget):
    def __init__(self, host='localhost', port='6600', **kwargs):
        super().__init__()
        self._host = host
        self._port = port
        self.time_to_next_update = 0
        self.timer = self._timer

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

        # Title and artist and filename
        # oh my
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

    def _timer(self):
            process = subprocess.Popen(
                shlex.split('mpc -h {} -p {} idle player'
                            .format(self._host, self._port)),
                stdout=subprocess.PIPE  # So we don't keep printing 'player'
            )
            try:
                process.wait(self.time_to_next_update)
            except subprocess.TimeoutExpired:
                process.kill()

    def update(self):
        try:
            data = self._get_data()

            if data['playing']:
                if not (data['title']):
                    text = '{}'.format(
                        '.'.join(path.basename(
                            data['filename']).split('.')[:-1]))
                else:
                    text = '{} - {}'.format(data['title'], data['artist'])

                # Drawing the underline progress bar
                text_length = len(text)
                self.progress = int(text_length *
                                    (data['position'] / data['length']))

                self.time_to_next_update = data['length'] / text_length
                return text
            else:
                self.time_to_next_update = 500
                return ''

        except:
            # Dirty fix for when mpd is not running
            # Bite me
            self.time_to_next_update = 2
            return ''

class BatteryWidget(Widget):
    def __init__(self):
        super().__init__()
        self.hide_value = 70
        self.bat_dir = '/sys/class/power_supply/BAT0/'
        self.timer = 60

    def _get_percentage(self):
        charge_full = int(open(self.bat_dir + 'charge_full').read())
        charge_now = int(open(self.bat_dir + 'charge_now').read())
        charge_percentage = (charge_now / charge_full) * 100
        return int(charge_percentage)

    def update(self):
        percentage = self._get_percentage()
        if percentage > self.hide_value:
            return ''
        else:
            return str(percentage)


class WiFiWidget(Widget):
    def __init__(self):
        super().__init__()
        self._adapter = 'wlp7s0'
        self.show_ip = False
        self.normal_icon = ''
        self.no_internet_icon = ''
        self.timer = 5

    def _get_essid(self):
        try:
            data = subprocess.getoutput('iwconfig ' + self._adapter)
            match = re.search('ESSID:"(.*)"', data)
            if match:
                return match.group(1).strip()
            else:
                return None
        except:
            return None

    def _get_ip(self):
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
                return ip

    def _internetp(self):
        s = requests.Session()
        s.mount('http://google.com', HTTPAdapter(max_retries=1))
        try:
            r = s.head('http://google.com', timeout=5)
        except:
            return False
        if r.status_code in (200, 302):
            return True
        return False

    def update(self):
        essid = self._get_essid()
        if essid:
            text = essid
        else:
            return ''

        if self.show_ip:
            ip = self._get_ip()
            text = '{} {}'.format(text, ip)

        # if self._internetp():
        #     self.icon = self.normal_icon
        # else:
        #     self.icon = self.no_internet_icon

        return text

class MailWidget(Widget):
    def __init__(self):
        super().__init__()
        self.timer = 10

    def update(self):
        count = int(subprocess.getoutput("unread"))
        running = True
        try:
            subprocess.check_call(["pgrep", "offlineimap"])
        except CalledProcessError:
            running = False

        if running and not count:
            return ""
        elif not running and not count:
            return "x"
        else:
            return count
