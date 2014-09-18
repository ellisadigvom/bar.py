#!/usr/bin/python
# Author: Ellis Adigvom ellisadigvom@gmail.com
# TODO: fix error checking for invalid font
from subprocess import PIPE, Popen, STDOUT, getoutput
import re

class Bar():
    def __init__(self, font=None, bg=None, fg=None, bottom=False,
                 separator='   ', padding=' ', icon_fg=None, icon_bg=None,
                 icon_separator=' ', **kwargs):
        self._separator = separator
        self._icon_separator = icon_separator
        self._padding = padding

        args = ['bar']
        xresources = self._get_xresources()
        self._attributes = {}

        if bg:
            bg = color_validate(bg)
        elif 'background' in xresources.keys():
            bg = color_validate(xresources['background'])
        if bg:
            args.append('-B')
            args.append(bg)
            self._bg = bg

        if fg:
            fg = color_validate(fg)
        elif 'foreground' in xresources.keys():
            fg = color_validate(xresources['foreground'])
        if fg:
            args.append('-F')
            args.append(fg)
            self._fg = fg

        if icon_bg:
            icon_bg = color_validate(icon_bg)
        elif 'icon.background' in xresources.keys():
            icon_bg = color_validate(xresources['icon.background'])
        if icon_bg:
            self._icon_bg = icon_bg

        if icon_fg:
            self._icon_fg = color_validate(icon_fg)
        elif 'icon.foreground' in xresources.keys():
            self._icon_fg = color_validate(xresources['icon.foreground'])
        if icon_fg:
            self._icon_fg = icon_fg

        if font:
            args.append('-f')
            args.append(font)
        elif 'font' in xresources.keys():
            args.append('-f')
            args.append(xresources['font'])

        if bottom:
            args.append('-b')

        #args.append('-u 0')
        self._args = args

    def start(self):
        ''' Start the bar process
        '''
        self._bar = Popen(self._args, stdin=PIPE, stdout=PIPE,
                          stderr=PIPE, universal_newlines=True)
        if self._bar.poll():
            error = self._bar.stderr.read().strip()
            raise ValueError(error)

    def get_pid(self):
        if self._bar:
            return self._bar.pid

    def _get_xresources(self):
        ''' Get data from panel.* xresources entries
        '''
        data = getoutput('xrdb -query')
        xresources = {}
        for i in data.splitlines():
            match = re.match('^panel\.(.+):\s+(.+)', i)
            if match:
                xresources[match.group(1)] = match.group(2)
        return xresources

    def _print_line(self, line):
        self._bar.stdin.write(line)
        self._bar.stdin.write('\n')
        self._bar.stdin.flush()

    def draw_widgets(self, left=None, center=None, right=None):
        ''' Print widgets to the appropriate positions on the bar
        '''
        if left == []:
            left_string = ''
        else:
            left_strings = [self.draw_widget(i) for i in left if i]
            left_string = self._separator.join(
                    [i for i in left_strings if i])

        if center == []:
            center_string = ''
        else:
            center_strings = [self.draw_widget(i) for i in center if i]
            center_string = self._separator.join(
                    [i for i in center_strings if i])

        if right == []:
            right_string = ''
        else:
            right_strings = [self.draw_widget(i) for i in right]
            right_string = self._separator.join(
                    [i for i in right_strings if i])

        line = ''.join(('%{l}', self._padding, left_string,
                        '%{c}', center_string,
                        '%{r}', right_string, self._padding))
        self._print_line(line)

    def draw_widget(self, widget):
        widget_dict = widget()
        if not widget_dict:
            return None
        ret_text = widget_dict['text']
        if widget_dict['bg']:
            bg = widget_dict['bg']
            ret_text = colorize(bg=bg, text=ret_text)

        if widget_dict['fg']:
            fg = widget_dict['fg']
            ret_text = colorize(fg=fg, text=ret_text)

        if widget_dict['icon']:
            icon = widget_dict['icon']
            if widget_dict['icon_bg']:
                icon_bg = widget_dict['icon_bg']
            else:
                icon_bg = self._icon_bg
            if icon_bg:
                icon = colorize(bg=icon_bg, text=icon)

            if widget_dict['icon_fg']:
                icon_fg = widget_dict['icon_fg']
            else:
                icon_fg = self._icon_fg
            if icon_fg:
                icon = colorize(fg=icon_fg, text=icon)
            ret_text = ''.join((icon, self._icon_separator, ret_text))
        return ret_text

def color_validate(color):
    ''' Takes anything that looks like it might be a hex color
        and changes it to the form #aarrggbb
    '''
    if not color:
        return None
    match = re.search('([a-f \d]{6}$)|([a-f \d]{8}$)', color)
    if not match:
        raise ValueError('Invalid color: ' + color)
    raw_color = match.group(0)
    if len(raw_color) == 8:
        return ''.join(('#', raw_color))
    elif len(raw_color) == 6:
        return ''.join(('#', 'ff', raw_color))
    else:
        raise ValueError('Invalid color')

def colorize(text, bg=None, fg=None):
    if fg:
        text = '%{{F{0}}}{1}%{{F-}}'.format(fg, text)
    if bg:
        text = '%{{B{0}}}{1}%{{B-}}'.format(bg, text)
    return text
