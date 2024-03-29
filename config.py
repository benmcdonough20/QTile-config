# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List  # noqa: F401

from libqtile import bar, layout, widget
from libqtile.config import Click, Drag, Group,  Match, Screen, ScratchPad, DropDown
from libqtile.config import EzKey as Key
from libqtile.lazy import lazy

import os
import subprocess
from libqtile import hook
from Xlib import display as xdisplay

from MutableScratch import MutableScratch

mod = 'mod4'

Key.modifier_keys = {
   'M': 'mod4',
   'A': 'mod1',
   'S': 'shift',
   'C': 'control'
}

keys = [
    Key("M-a", lazy.group['scratchpad'].dropdown_toggle('term')),

    Key("M-h", lazy.layout.left()),
    Key("M-l", lazy.layout.right()),
    Key("M-j", lazy.layout.down()),
    Key("M-k", lazy.layout.up()),

    # Mocing windows between columns
    Key("M-S-h", lazy.layout.shuffle_left()),
    Key("M-S-l", lazy.layout.shuffle_right()),
    Key("M-S-j", lazy.layout.shuffle_down()),
    Key("M-S-k", lazy.layout.shuffle_up()),

    # Grow windows.
    Key("M-C-h", lazy.layout.grow_left()),
    Key("M-C-l", lazy.layout.grow_right()),
    Key("M-C-j", lazy.layout.grow_down()),
    Key("M-A-j", lazy.layout.increase_ratio()),
    Key("M-C-k", lazy.layout.grow_up()),
    Key("M-A-k", lazy.layout.decrease_ratio()),
    Key("M-n", lazy.layout.normalize()),

    # Toggle between split and unsplit sides of stack.
    Key("M-S-<Return>", lazy.layout.toggle_split()),

    # Toggle between different layouts as defined below
    Key("M-<Up>", lazy.next_layout()),

    #OS commands
    #Key("M-d", lazy.spawn("rofi -show run -theme ~/colors-rofi-dark.rasi")),
    Key("M-d", lazy.spawn("rofi -show run -theme /usr/share/rofi/themes/Arc.rasi")),
    #Key("M-w", lazy.spawn("rofi -show window -theme ~/colors-rofi-dark.rasi")),
    Key("M-w", lazy.spawn("rofi -show window -theme /usr/share/rofi/themes/Arc.rasi")),
    Key("M-S-q", lazy.window.kill()),
    Key("M-C-r", lazy.restart()),
    Key("M-C-q", lazy.shutdown()),
    Key("M-r", lazy.spawncmd(prompt = "λ")),
    Key("M-n", lazy.screen.widget['prompt'].exec_general('name', 'group', 'set_label')),#lazy.group.set_label("new_label")),
    Key("M-<space>", lazy.screen.next_group()),
    Key("M-C-<space>", lazy.screen.prev_group()),

    #Applications
    Key("M-C-1", lazy.spawn("telegram-desktop")),
    Key("M-C-2", lazy.spawn("firefox")),
    Key("M-C-3", lazy.spawn("thunar")),
    Key("M-C-4", lazy.spawn("code")),
    Key("M-C-5", lazy.spawn("discord")),
    Key("M-<Return>", lazy.spawn("urxvt")),

    Key("M-f", lazy.window.toggle_floating()),
    Key("M-<Tab>", lazy.screen.next_group()),
    Key("M-C-<Tab>", lazy.screen.prev_group()),
    Key("M-m", lazy.hide_show_bar("top")),
    Key("M-C-m", lazy.hide_show_bar("bottom")),

    #New dunstctl controls
    Key("A-<space>", lazy.spawn("dunstctl close")),
    Key("C-A-<space>", lazy.spawn("dunstctl close-all")),
]


groups=[Group(i) for i in "123456789"]

for i in groups:
    keys.extend([
        # mod1 + letter of group = switch to group
        Key("M-" + i.name, lazy.group[i.name].toscreen()),

        # mod1 + shift + letter of group = switch to & move focused window to group
        Key("M-S-" + i.name, lazy.window.togroup(i.name, switch_group=True)),
        # Or, use below if you prefer not to switch to that group.
        # # mod1 + shift + letter of group = move focused window to group
        # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
        #     desc="move focused window to group {}".format(i.name)),
    ])

groups.append(ScratchPad("ranger", [DropDown("file manager", "urxvt -hold -e 'ranger'",x=0.05, y=0.4, width=0.9, height=0.6, opacity=0.9, on_focus_lost_hide=True)]))
#Define colors
background = "#282c34"
foreground = "#dcdfe4"
black=   '#1a181c'
red=     '#e06c75'
green=   '#e06c75'
yellow=  '#98c379'
blue=    '#e5c07b'
magenta= '#bb60ea'
cyan=    '#149bda'
white = '#bcbabe'

layouts = [
    layout.Columns(border_focus = "#514b57",
        border_normal = background,
        #margin = 6,
        border_width=1),
    layout.Max(),
    layout.Tile(border_focus = "#514b57",
        borner_normal = background,
        #margin = 6,
        border_width = 1)
]

widget_defaults = dict(
    font='Hack Nerd Font',
    fontsize=14,
    padding=3,
    background = background,
    foreground = foreground
)

extension_defaults = widget_defaults.copy()

#See https://github-wiki-see.page/m/qtile/qtile/wiki/screens

def get_num_monitors():
    num_monitors = 0
    try:
        display = xdisplay.Display()
        screen = display.screen()
        resources = screen.root.xrandr_get_screen_resources()

        for output in resources.outputs:
            monitor = display.xrandr_get_output_info(output, resources.config_timestamp)
            preferred = False
            if hasattr(monitor, "preferred"):
                preferred = monitor.preferred
            elif hasattr(monitor, "num_preferred"):
                preferred = monitor.num_preferred
            if preferred:
                num_monitors += 1
    except Exception as e:
        # always setup at least one monitor
        return 1
    else:
        return num_monitors

#TODO: code button widet to open prompt

screens = [
    Screen(
        bottom=bar.Bar(
            [
                widget.Prompt(background = red, foreground = background),
                widget.GroupBox(
                            highlight_method = 'block',
                            rounded = False,
                            block_highlight_text_color = background,
                            this_current_screen_border = foreground,
                            other_screen_border = blue,
                            urgent_border = red,
                            other_current_screen_border = blue,
                            this_screen_border = foreground,
                    ),
                widget.WindowName(max_chars = 70),
                widget.CPU(format = ' 龍 {freq_current}GHz {load_percent}%',
                    ),
                widget.TextBox(' '),
                widget.ThermalSensor(threshold = 85,
                ),
                widget.Memory(
                    format = ' {MemUsed: .2f}{mm}',
                    measure_mem = 'G',
                    ),
                widget.Clock(format='  %I:%M %p',
                    ),
                widget.Battery(format = ' {char}{percent: 2.0%}',
                   charge_char = '',
                   discharge_char = '',
                   empty_char = '',
                   full_char = '',
                   show_short_text = False,
                   ),
                widget.Backlight(
                    format = '  {percent:2.0%}',
                    backlight_name = 'intel_backlight',
                    ),
                widget.Sep(linewidth=0,padding=10,foreground=cyan),
                widget.Systray(),
            ],
            30,
            ),
             top = bar.Bar([widget.TaskList(
                title_width_method = 'uniform',
                #markup=True,
                highlight_method = 'block',
                #markup_focused = "<span foreground=\"black\">{}</span>",
                icon_size = 0,
                border ="#3b404c",
                rounded= False,
                txt_minimized = " ",
                )],22)
)]

num_monitors = get_num_monitors()

if num_monitors > 1:
    for m in range(num_monitors-1):
        screens.append(
                Screen(
                    top = bar.Bar([widget.TaskList(
                title_width_method = 'uniform',
                #markup=True,
                highlight_method = 'block',
                #markup_focused = "<span foreground=\"black\">{}</span>",
                icon_size = 0,
                border ="#3b404c",
                rounded= False,
                txt_minimized = " ",
                )],22),
                bottom = bar.Bar(
                        [widget.Prompt(background = red, foreground = background),
                        widget.GroupBox(
                            highlight_method = 'block',
                            rounded = False,
                            block_highlight_text_color = background,
                            this_current_screen_border = foreground,
                            other_screen_border = blue,
                            urgent_border = red,
                            other_current_screen_border = blue,
                            this_screen_border = foreground,
                    ),
                        widget.WindowName()], 30)
                    )
                )

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    *layout.Floating.default_float_rules,
    Match(wm_class='confirmreset'),  # gitk
    Match(wm_class='makebranch'),  # gitk
    Match(wm_class='maketag'),  # gitk
    Match(wm_class='ssh-askpass'),  # ssh-askpass
    Match(title='branchdialog'),  # gitk
    Match(title='pinentry'),  # GPG key password entry
    Match(wm_class='blueman-manager'),
    Match(wm_class='pavucontrol'),
],
border_focus = "#514b57",
border_normal = background)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

wmname = "LG3D"

@hook.subscribe.startup_once
def autostart():
    hom = os.path.expanduser('~/setup_qtile.sh')
    subprocess.run([home])

#copying i3 scratch behavior using https://github.com/jrwrigh/qtile-mutable-scratch

mutscr = MutableScratch()
groups.append(Group('')) #adds an invisible group

keys.extend( [
    Key('M-S-<minus>', mutscr.add_current_window()),
    Key('M-<minus>', mutscr.toggle()),
    Key('M-C-<minus>', mutscr.remove()),
])

hook.subscribe.startup_complete(mutscr.qtile_startup)
