#!/usr/bin/python
# Author: Ellis Adigvom ellisadigvom@gmail.com
from subprocess import PIPE, Popen, getoutput
import re

class Bar():
    def __init__(self, separator='   ', padding=' ', icon_separator=' '):
        self._widgets = {'left': [], 'center': [], 'right': []}

        xresources = self._get_xresources()
        self.resources = xresources

        self.resources['separator'] = separator
        self.resources['icon_separator'] = icon_separator
        self.resources['padding'] = padding
        self._colors = {}

        self._bar = self.start()

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

        bar = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                universal_newlines=True)
        if bar.poll():
            error = self._bar.stderr.read().strip()
            raise ValueError(error)
        return bar

    def register(self, widget, position):
        self._widgets[position].append(widget)

    def get_pid(self):
        if self._bar:
            return self._bar.pid

    #TODO: Do the wildcards thing
    def _get_xresources(self, wildcardresources=[]):
        ''' Get data from panel.* xresources entries,
            or wildcard entries we want
        '''
        data = getoutput('xrdb -query')
        xresources = {}
        for i in data.splitlines():
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
        self._bar.stdin.write(line)
        self._bar.stdin.write('\n')
        self._bar.stdin.flush()

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
            raise ValueError('Invalid color: ' + color)
        raw_color = match.group(0)
        if len(raw_color) == 8:
            return ''.join(('#', raw_color))
        elif len(raw_color) == 6:
            return ''.join(('#', 'ff', raw_color))

    #TODO: The rest of the formatting options
    def format(self, text, background=None, foreground=None, underline=False, overline=False,
            underline_color=None, invert=False):
        for i in (background, foreground, underline_color):
            i = self.bar.color_validate(i)

        if foreground:
            text = '%{{F{0}}}{1}%{{F-}}'.format(foreground, text)
        if background:
            text = '%{{B{0}}}{1}%{{B-}}'.format(background, text)
        if underline:
            pass
        if overline:
            pass
        if underline_color:
            pass
        if invert:
            pass
        return text
