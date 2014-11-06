#!/usr/bin/python
# Author: Ellis Adigvom ellisadigvom@gmail.com
from subprocess import PIPE, Popen, getoutput
import re
import threading
#TODO: The rest of the clicky stuff

class Bar():
    _wildcard_resources = ['background', 'foreground']
    def __init__(self, separator='   ', padding=' ', icon_separator=' '):
        self._widgets = {'left': [], 'center': [], 'right': []}
        
        xresources = self._get_xresources()
        self.resources = xresources

        self.resources['separator'] = separator
        self.resources['icon_separator'] = icon_separator
        self.resources['padding'] = padding
        self._colors = {}

        self._bar_process = self.start()
        self._listen_thread = threading.Thread(target=self.click_listener)
        self._listen_thread.start()

    def start(self):
        ''' Start the bar process
        '''
        args = ['bar']

        background = self.color_validate('background')
        if background:
            args.append('-B')
            args.append(background)

        foreground = self.color_validate('foreground')
        if foreground:
            args.append('-F')
            args.append(foreground)

        font = self.resources.get('font')
        if font:
            args.append('-f')
            args.append(font)

        if self.resources.get('position') == 'bottom':
            args.append('-b')

        underline_height = self.resources.get('underline.height')
        if underline_height:
            args.append('-u')
            args.append(underline_height)

        bar_process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                universal_newlines=True)
        if bar_process.poll():
            error = bar_process.stderr.read().strip()
            raise ValueError(error)
        return bar_process

    def click_listener(self):
        while 1:
            line = self._bar_process.stdout.readline().strip()
            prefix = line.split()[0]
            arguments = line.split()[1:]
            widgets = []
            [widgets.extend(i) for i in self._widgets.values()]
            for i in widgets:
                if int(prefix) == i.__hash__():
                    i.click_handler(arguments)
                    break

    def register(self, widget, position):
        self._widgets[position].append(widget)

    def get_pid(self):
        if self._bar_process:
            return self._bar_process.pid

    #TODO: Get colors and store them with sensible names
    #TODO: Decide whether to use the two regexps or one monster one
    def _get_xresources(self):
        ''' Get data from panel.* xresources entries,
            or wildcard entries we want
        '''
        data = getoutput('xrdb -query')
        xresources = {}
        for i in data.splitlines():
            # Wildcard resources
            match = re.match('\*\.(\w+):\s+(.+)', i)
            if match:
                key = match.group(1)
                value = match.group(2)
                if match.group(1) in self._wildcard_resources:
                    xresources[key] = value
                    
            # Resources starting with 'panel'
            match = re.match('^panel\.(.+):\s+(.+)', i)
            #match = re.match('^panel\.(.+):\s+[\' "]?(.+)[\' "]?', i)
            if match:
                key = match.group(1)
                value = match.group(2)
                match = re.match('^[\' "](.*)[\' "]$', value)
                if match:
                    value = match.group(1)
                xresources[key] = value
        return xresources

    def _print_line(self, line):
        """ Write a line of text to the bar. That is all.
        """
        self._bar_process.stdin.write(line)
        self._bar_process.stdin.write('\n')
        self._bar_process.stdin.flush()

    def redraw(self):
        ''' Print widgets to the appropriate positions on the bar
        '''
        if self._widgets['left'] == []:
            left_string = ''
        else:
            left_string = self.resources['separator'].join(
                    [i.text for i in self._widgets['left'] if i.text])

        if self._widgets['center'] == []:
            center_string = ''
        else:
            center_string = self.resources['separator'].join(
                    [i.text for i in self._widgets['center'] if i.text])

        if self._widgets['right'] == []:
            right_string = ''
        else:
            right_string = self.resources['separator'].join(
                    [i.text for i in self._widgets['right'] if i.text])

        line = ''.join(('%{l}', self.resources['padding'], left_string,
                        '%{c}', center_string,
                        '%{r}', right_string, self.resources['padding']))
        self._print_line(line)

    def color_validate(self, color, skipresources=False):
        ''' Takes anything that looks like it might be a color
            and changes it to the form #aarrggbb
        '''
        if not color:
            return None

        if color in self._colors:
            return self._colors[color]
        elif color in self.resources.keys() and not skipresources:
            color_value = self.color_validate(self.resources[color],
                    skipresources=True)
            self._colors[color] = color_value
            return color_value

        match = re.search('([a-f \d]{6}$)|([a-f \d]{8}$)', color)
        if not match:
            return None
            #raise ValueError('Invalid color: ' + color)
        raw_color = match.group(0)
        if len(raw_color) == 8:
            return ''.join(('#', raw_color))
        elif len(raw_color) == 6:
            return ''.join(('#', 'ff', raw_color))

    #TODO: The rest of the formatting options
    def format(self, text, background=None, foreground=None, underline=False,
            overline=False, line_color=None, invert=False):
        """ Format text according to the options given using bar's syntax
        """
        for i in (background, foreground, line_color):
            i = self.color_validate(i)

        if foreground:
            text = '%{{F{0}}}{1}%{{F-}}'.format(foreground, text)
        if background:
            text = '%{{B{0}}}{1}%{{B-}}'.format(background, text)
        if underline or overline:
            if underline:
                text = '%{{+u}}{}%{{-u}}'.format(text)
            if overline:
                text = '%{{+o}}{}%{{-o}}'.format(text)
            if not line_color:
                if 'line_color' in self.resources.keys():
                    line_color = self.color_validate('line_color')
                elif 'foreground' in self.resources.keys():
                    line_color = self.color_validate('foreground')
            text = '%{{U{0}}}{1}%{{U-}}'.format(line_color, text)

        if invert:
            text = '%{{R}}{}%{{R}}'.format(text)
        return text

    def make_clickable(self, text, args, widget, button=''):
        widget_hash = widget.__hash__()
        text = '%{{A{}:{} {}:}}{}%{{A}}'.format(button, widget_hash, args, text)
        return text
