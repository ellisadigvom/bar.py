from time import strftime, sleep
from subprocess import getoutput
from mpd import MPDClient, ConnectionError
import re
from itertools import zip_longest
import threading

#TODO: Clean up init methods
class Widget(threading.Thread):
    def __init__(self, bar=None, position='center', icon=None):
        if not bar: raise ValueError
        self._bar = bar
        self.text = ''
        bar.register(self, position=position)
        super().__init__()
        self.start()

    def _format_icon(self):
        # Color the icon and whatever at widget init
        pass

    def _iconify(self):
        if self._icon:
            self.text = '{}{}{}'.format(self._icon,  self._bar.resources['icon_separator'],
                    self.text)

class StaticTextWidget():
    def __init__(self, text):
        self._text = text

class ClockWidget(Widget):
    def __init__(self, format='%a %d %b %H:%M', icon='È', **kwargs):
        self._icon = icon
        self._format = format
        self.text = 'this should not happen'
        super().__init__(**kwargs)

    def run(self):
        first_run = True
        while 1:
            self.text = strftime(self._format)
            self._iconify()
            self._bar.redraw()
            if first_run:
                seconds = int(strftime('%S'))
                sleep(seconds + 1)
                first_run = False
            else:
                sleep(60)


#class BatteryWidget(Widget):
    #def __init__(self, show_value=70, **kwargs):
        #super().__init__(**kwargs)
        #self._show_value = show_value

    #def _get_percentage(self):
        #charge_full = int(open('/sys/class/power_supply/BAT1/charge_full').read())
        #charge_now = int(open('/sys/class/power_supply/BAT1/charge_now').read())
        #charge_percentage = (charge_now / charge_full) * 100
        #return int(charge_percentage)

    #def __call__(self):
        #percentage = self._get_percentage()
        #if percentage > self._show_value:
            #return None
        #ret_dict = super().__call__()
        #ret_dict['text'] = str(percentage)
        #return ret_dict

#class WiFiWidget(Widget):
    #def __init__(self, adapter='wlp2s0', **kwargs):
        #super().__init__(**kwargs)
        #self._adapter = adapter

    #def _get_essid(self):
        #data = getoutput('iwconfig ' + self._adapter)
        #match = re.search('ESSID:"(.*)"', data)
        #if match:
            #return match.group(1)
        #else:
            #return None

    #def __call__(self):
        #essid = self._get_essid()
        #if not essid:
            #return None
        #ret_dict = super().__call__()
        #ret_dict['text'] = essid
        #return ret_dict

#class MpdWidget(Widget):
    #def __init__(self, host='localhost', port='6600', **kwargs):
        #super().__init__(**kwargs)
        #self._host=host
        #self._port=port

    #def _get_data(self):
        #title = None
        #artist = None
        #playing = False
        #mpc_output = getoutput('mpc status --format {} -h {} -p {}'.format(
            #'%title%---%artist%', self._host, self._port))
        #lines = mpc_output.splitlines()
        #if len(lines) == 1:    # stopped
            #return {'title': '', 'artist': '', 'playing': False}

        #match = re.match('^(.*)---(.*)$', lines[0])
        #if match:
            #title = match.group(1)
            #artist = match.group(2)

        #match = re.match('\[(.+)\]', lines[1])
        #if match:
            #if match.group(1) == 'playing':
                #playing = True
            #elif match.group(1) == 'paused':
                #playing = False
        #return {'title': title, 'artist': artist, 'playing': playing}

    #def __call__(self):
        #data = self._get_data()
        #if not data['playing']:
            #return None
        #ret_dict = super().__call__()
        #text = ' - '.join((data['title'], data['artist']))
        #ret_dict['text'] = text
        #return ret_dict

#class WorkspaceWidget(Widget):
    #def __init__(self, workspace_labels=[], active_background=None, active_foreground=None,
            #workspace_separator=' ', **kwargs):
        #super().__init__(**kwargs)
        #self._active_background = color_validate(active_background)
        #self._active_foreground = color_validate(active_foreground)
        #self._workspace_separator = workspace_separator
        #workspaces = getoutput('bspc query -D').splitlines()
        #workspaces = [i.strip() for i in workspaces]
        #self._workspaces = workspaces
        #self._labels = workspace_labels

    #def __call__(self):
        #ret_dict = super().__call__()
        #active_workspace = getoutput('bspc query -D -d').strip()
        #text = ''
        #for workspace, label in zip_longest(self._workspaces, self._labels,
                #fillvalue=None):
            #if not workspace: break
            #this_workspace = label or workspace 
            #if workspace == active_workspace:
                #if self._active_background:
                    #this_workspace = colorize(text=this_workspace, background = self._active_background)
                #if self._active_foreground:
                    #this_workspace = colorize(text=this_workspace, foreground = self._active_foreground)
            #text = self._workspace_separator.join((text, this_workspace))
        #ret_dict['text'] = text
        #return ret_dict

