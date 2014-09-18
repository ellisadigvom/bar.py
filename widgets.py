from time import strftime
from bar import color_validate, colorize
from subprocess import getoutput
from mpd import MPDClient, ConnectionError
import re
from itertools import zip_longest

class Widget():
    def __init__(self, bg=None, fg=None,
                 icon=None, icon_bg=None, icon_fg=None):
        self._bg = color_validate(bg)
        self._fg = color_validate(fg)
        self._icon = icon
        self._icon_bg = color_validate(icon_bg)
        self._icon_fg = color_validate(icon_fg)

    def __call__(self):
        ret_dict = {}
        ret_dict['bg'] = self._bg
        ret_dict['fg'] = self._fg
        ret_dict['icon'] = self._icon
        ret_dict['icon_bg'] = self._icon_bg
        ret_dict['icon_fg'] = self._icon_fg
        return ret_dict

class StaticTextWidget(Widget):
    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self._text = text

    def __call__(self):
        ret_dict = super().__call__()
        ret_dict['text'] = self._text
        return ret_dict

class ClockWidget(Widget):
    def __init__(self, format='%a %d %b %H:%M', **kwargs):
        super().__init__(**kwargs)
        self._format = format

    def __call__(self):
        ret_dict = super().__call__()
        ret_dict['text'] = strftime(self._format)
        return ret_dict

class BatteryWidget(Widget):
    def __init__(self, show_value=70, **kwargs):
        super().__init__(**kwargs)
        self._show_value = show_value

    def _get_percentage(self):
        charge_full = int(open('/sys/class/power_supply/BAT1/charge_full').read())
        charge_now = int(open('/sys/class/power_supply/BAT1/charge_now').read())
        charge_percentage = (charge_now / charge_full) * 100
        return int(charge_percentage)

    def __call__(self):
        percentage = self._get_percentage()
        if percentage > self._show_value:
            return None
        ret_dict = super().__call__()
        ret_dict['text'] = str(percentage)
        return ret_dict

class WiFiWidget(Widget):
    def __init__(self, adapter='wlp2s0', **kwargs):
        super().__init__(**kwargs)
        self._adapter = adapter

    def _get_essid(self):
        data = getoutput('iwconfig ' + self._adapter)
        match = re.search('ESSID:"(.*)"', data)
        if match:
            return match.group(1)
        else:
            return None

    def __call__(self):
        essid = self._get_essid()
        if not essid:
            return None
        ret_dict = super().__call__()
        ret_dict['text'] = essid
        return ret_dict

class MpdWidget(Widget):
    def __init__(self, host='localhost', port='6600', **kwargs):
        super().__init__(**kwargs)
        self._host=host
        self._port=port

    def _get_data(self):
        title = None
        artist = None
        playing = False
        mpc_output = getoutput('mpc status --format {} -h {} -p {}'.format(
            '%title%---%artist%', self._host, self._port))
        lines = mpc_output.splitlines()
        if len(lines) == 1:    # stopped
            return {'title': '', 'artist': '', 'playing': False}

        match = re.match('^(.*)---(.*)$', lines[0])
        if match:
            title = match.group(1)
            artist = match.group(2)

        match = re.match('\[(.+)\]', lines[1])
        if match:
            if match.group(1) == 'playing':
                playing = True
            elif match.group(1) == 'paused':
                playing = False
        return {'title': title, 'artist': artist, 'playing': playing}

    def __call__(self):
        data = self._get_data()
        if not data['playing']:
            return None
        ret_dict = super().__call__()
        text = ' - '.join((data['title'], data['artist']))
        ret_dict['text'] = text
        return ret_dict

class WorkspaceWidget(Widget):
    def __init__(self, workspace_labels=[], active_bg=None, active_fg=None,
            workspace_separator=' ', **kwargs):
        super().__init__(**kwargs)
        self._active_bg = color_validate(active_bg)
        self._active_fg = color_validate(active_fg)
        self._workspace_separator = workspace_separator
        workspaces = getoutput('bspc query -D').splitlines()
        workspaces = [i.strip() for i in workspaces]
        self._workspaces = workspaces
        self._labels = workspace_labels

    def __call__(self):
        ret_dict = super().__call__()
        active_workspace = getoutput('bspc query -D -d').strip()
        text = ''
        for workspace, label in zip_longest(self._workspaces, self._labels,
                fillvalue=None):
            if not workspace: break
            this_workspace = label or workspace 
            if workspace == active_workspace:
                if self._active_bg:
                    this_workspace = colorize(text=this_workspace, bg = self._active_bg)
                if self._active_fg:
                    this_workspace = colorize(text=this_workspace, fg = self._active_fg)
            text = self._workspace_separator.join((text, this_workspace))
        ret_dict['text'] = text
        return ret_dict

