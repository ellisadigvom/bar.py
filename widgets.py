from time import strftime, sleep
from subprocess import getoutput, Popen, PIPE
from mpd import MPDClient, ConnectionError
import re
from itertools import zip_longest
import threading

#TODO: Clean up init methods
class Widget(threading.Thread):
    def __init__(self, bar, position='center', icon=None):
        if not bar:
            raise ValueError
        self._bar = bar
        self._icon = icon
        self.text = ''
        bar.register(self, position=position)
        self._format_icon()
        super().__init__()
        self.start()

    def _format_icon(self):
        # Color the icon and whatever at widget init
        pass

    def _iconify(self):
        if self._icon:
            self.text = '{}{}{}'.format(self._icon,
                self._bar.resources['icon_separator'], self.text)

class SkeletonWidget(Widget):
    def __init__(self, **kwargs):
        # Do init stuff here
        super().__init__(**kwargs)

    def run(self):
        pass

class StaticTextWidget():
    def __init__(self, text):
        self._text = text

#TODO: What happens when we put the computer to sleep?
class ClockWidget(Widget):
    def __init__(self, format='%a %d %b %H:%M', icon='È', **kwargs):
        self._format = format
        self.text = 'this should not happen'
        super().__init__(icon=icon, **kwargs)

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
        bspc_subscribe = Popen (['bspc', 'control', '--subscribe'],
                stdout=PIPE, stderr=PIPE, universal_newlines=True)
        while 1:
            text = ''
            line = bspc_subscribe.stdout.readline()
            workspaces = line.split(':')[1:-1]
            for workspace, label in zip_longest(workspaces, self._labels):
                active = False
                occupied = False
                if re.match('[A-Z]', workspace):    # TODO: regexps are probably overkill
                    active = True
                if re.match('[o, O]', workspace):
                    occupied = True

                if label:
                    workspace_text = ' {} '.format(label)
                else:
                    workspace_text = ' {} '.format(workspace[1:])
                if active:
                    workspace_text = self._bar.format(workspace_text, invert=True)
                text += workspace_text
            self.text = text
            self._bar.redraw()

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


