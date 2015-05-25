#!/usr/bin/python
# Author: Ellis Adigvom ellisadigvom@gmail.com
from subprocess import PIPE, Popen, getoutput
import re
import threading
# TODO: The rest of the clicky stuff


class Bar():
    def __init__(self):
        self._widgets = {'left': [], 'center': [], 'right': []}

        self.background = 'background'
        self.foreground = 'foreground'

        self.height = ''
        self.width = ''
        self.xoffset = ''
        self.yoffset = ''

        self.separator = ''
        self.padding = ' '
        self.icon_separator = ' '
        self.font = None
        self.position = 'top'

        self._colors = {}
        self._colors = {k: self.color(v) for (k, v)
                        in get_xresources().items()}

    def start(self):
        ''' Start the bar process
        '''
        args = ['lemonbar']

        background = self.color(self.background)
        if background:
            args.append('-B')
            args.append(background)

        foreground = self.color(self.foreground)
        if foreground:
            args.append('-F')
            args.append(foreground)

        if self.font:
            args.append('-f')
            if type(self.font) == list:
                args.append(','.join(self.font))
            else:
                args.append(self.font)

        if self.position == 'bottom':
            args.append('-b')

        if self.height or self.width or self.xoffset or self.yoffset:
            args.append('-g')
            args.append('{}x{}+{}+{}'.format(self.width,
                                             self.height,
                                             self.xoffset,
                                             self.yoffset))

        bar_process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                            universal_newlines=True)
        if bar_process.poll():
            error = bar_process.stderr.read().strip()
            raise ValueError(error)

        self._bar_process = bar_process
        self._listen_thread = threading.Thread(target=self.click_listener)
        self._listen_thread.start()

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

    def add(self, widget, position):
        if position.lower in ['left', 'l']:
            self._widgets['left'].append(widget)
        if position.lower in ['center', 'c']:
            self._widgets['center'].append(widget)
        if position.lower in ['right', 'r']:
            self._widgets['right'].append(widget)

    def get_pid(self):
        if self._bar_process:
            return self._bar_process.pid

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
            left_string = self.separator.join(
                [self.draw_widget(i) for i in self._widgets['left'] if i.text])

        if self._widgets['center'] == []:
            center_string = ''
        else:
            center_string = self.separator.join(
                [self.draw_widget(i) for i in
                    self._widgets['center'] if i.text])

        if self._widgets['right'] == []:
            right_string = ''
        else:
            right_string = self.separator.join(
                [self.draw_widget(i) for i in
                    self._widgets['right'] if i.text])

        line = ''.join(('%{l}', left_string,
                        '%{c}', center_string,
                        '%{r}', right_string))
        self._print_line(line)

    def draw_widget(self, widget):
        s = "{}{}{}".format(self.padding, widget.text, self.padding)
        return self.format(s, widget.background, widget.foreground,
                           line_color=widget.line_color)

    def color(self, color, skip_defaults=False):
        ''' Takes anything that looks like it might be a color
            and changes it to the form #aarrggbb
        '''
        if not color:
            return None

        if not skip_defaults:
            if color in ['background', 'foreground']:
                return self.color(self.__getattribute__(color),
                                  skip_defaults=True)

        # Check color dictionary
        if color in self._colors:
            return self._colors[color]

        match = re.search('([a-f \d]{6}$)|([a-f \d]{8}$)', color)
        if not match:
            return None
        raw_color = match.group(0)
        if len(raw_color) == 8:
            return ''.join(('#', raw_color))
        elif len(raw_color) == 6:
            return ''.join(('#', 'ff', raw_color))

    def format(self, text, background=None, foreground=None, underline=False,
               overline=False, line_color=None, invert=False):
        """ Format text according to the options given using bar's syntax
        """
        foreground = self.color(foreground)
        background = self.color(background)
        line_color = self.color(line_color)
        for i in (background, foreground, line_color):
            i = self.color(i)

        if foreground:
            text = wrap('F'+foreground, text, 'F-')
        if background:
            text = wrap('B'+background, text, 'B-')
        if underline or overline:
            if underline:
                text = wrap('+u', text, '-u')
            if overline:
                text = wrap('+o', text, '-o')
            if line_color:
                text = wrap('U'+line_color, text, 'U-')

        if invert:
            text = wrap('R', text, 'R')
        return text

    def make_clickable(self, text, args, widget, button=''):
        widget_hash = widget.__hash__()
        text = wrap('A{}:{} {}:'.format(button, widget_hash, args), text, 'A')

        return text


def wrap(o, text, c):
    return '%{{{}}}{}%{{{}}}'.format(o, text, c)


def get_xresources():
    data = getoutput('xrdb -query')
    xresources = {}
    colors = ['black', 'dark_red', 'dark_green', 'dark_yellow',
              'dark_blue', 'dark_magenta', 'dark_cyan', 'light_grey',
              'dark_grey', 'red', 'green', 'yellow', 'blue',
              'magenta', 'cyan', 'white']
    for i in data.splitlines():
        # Color definitions
        match = re.match('\*\.?(\w+):\s+(.+)', i)
        if match:
            key = match.group(1)
            value = match.group(2)
            if re.match('^color\d+', key):
                xresources[key] = value
            if key in ['background', 'foreground']:
                xresources[key] = value

    def parse_key(key):
        m = re.match('color(\d+)', key)
        if m:
            return colors[int(m.group(1))]
        else:
            return key

    return {parse_key(k): v for (k, v) in xresources.items()}
