from libqtile import bar, widget, layout
from libqtile.config import Screen, hook, Group, Drag, Click
from libqtile.config import EzKey as Key
from libqtile.command import lazy
from typing import List

#color scheme

GRAY = "#242434"
BLACK = "#111121"
PRIMARY = "#256c70"
SECONDARY = "#5e9f65"
TERTIARY = "#842759"
WHITE = "#909090"

#custom methods

#generates a cool separator
def _separator(_foreground, _background, direction="right"):
    if(direction is "right"):
        sep_char = '◣'
    else:
        sep_char = '◢'

    return widget.TextBox(
        text = sep_char,
        foreground = _foreground,
        font = 'Arial',
        fontsize = 60,
        padding = -5,
        background = _background
    )

#focuses a group if it is visible, switches to it if otherwise
def focus_or_switch(group_name):
    @lazy.function
    def _inner(qtile):
        groups = [s.group.name for s in qtile.screens]
        
        try:
            index = groups.index(group_name)
            qtile.toScreen(index)
        except ValueError:
            qtile.currentScreen.setGroup(qtile.groupMap[group_name])

    return _inner

#rotates focus between screens
def rot_focus(increment = 1):
    @lazy.function
    def _inner(qtile):
        qtile.toScreen( (qtile.currentScreen.index+increment)%len(qtile.screens) )
            
    return _inner

#rotates screens
def rot_screens(increment = 1):
    @lazy.function
    def _inner(qtile):

        current_groups = [s.group for s in qtile.screens]
        i = 0

        for s in qtile.screens:
            s.setGroup( current_groups[(i+increment) % len(current_groups)] )
            i+=1

    return _inner

#renames the current group using the prompt widget
def rename_group():
    @lazy.function
    def _inner(qtile):
        current_group = qtile.currentScreen.group
        qtile.widgetMap['prompt'].startInput(prompt="name", 
                callback=current_group.cmd_set_label)

    return _inner

#helper functions for the max layout feature
#TODO:read off parameters from qtile for extensibility
def rot_layout(increment = 1):
    @lazy.function
    def _inner(qtile):
        current_group = qtile.currentScreen.group
        layout_index = current_group.currentLayout

        if( increment is 1 and layout_index in [6,3]):
            current_group.toLayoutIndex((layout_index+2)%7)
        elif( increment is -1 and layout_index in [1,5]):
            current_group.toLayoutIndex((layout_index-2)%7)
        else:
            current_group.toLayoutIndex((layout_index+increment)%7)

    return _inner

def fullscreen_mode(direction = "right"):
    @lazy.function
    def _inner(qtile):
        if( direction is "right" ):
            qtile.currentScreen.group.toLayoutIndex(4)
        else:
            qtile.currentScreen.group.toLayoutIndex(0)
        
    return _inner

#key bindings

modifier_keys = {
    'M': 'mod4',
    'A': 'mod1',
    'S': 'shift',
    'C': 'control'
}

mod = 'mod4'

keys = [

    Key("M-n", rename_group()),
    Key("M-C-<bracketright>", fullscreen_mode()),
    Key("M-C-<bracketleft>", fullscreen_mode("left")),

    Key("M-<bracketleft>", rot_focus(-1)),
    Key("M-<bracketright>", rot_focus()),
    Key("M-S-<bracketleft>", rot_screens(-1)),
    Key("M-S-<bracketright>", rot_screens()),
    Key("M-<Up>", lazy.layout.down()),
    Key("M-<Down>", lazy.layout.up()),
    Key("M-<Left>", lazy.layout.left()),
    Key("M-<Right>", lazy.layout.right()),

    Key("M-A-<Up>", lazy.layout.flip_up()),
    Key("M-A-<Left>", lazy.layout.flip_left()),
    Key("M-A-<Down>", lazy.layout.flip_down()),
    Key("M-A-<Right>", lazy.layout.flip_right()),

    Key("M-S-<Up>", lazy.layout.shuffle_up()),
    Key("M-S-<Left>", lazy.layout.shuffle_left(), lazy.layout.swap_left(), lazy.layout.client_to_previous()),
    Key("M-S-<Down>", lazy.layout.shuffle_down()),
    Key("M-S-<Right>", lazy.layout.shuffle_right(), lazy.layout.swap_right(), lazy.layout.client_to_next()),

    Key("M-S-<minus>", lazy.layout.normalize()),
    Key("M-S-<equal>", lazy.layout.maximize()),
    Key("M-<minus>", lazy.layout.grow()),
    Key("M-<equal>", lazy.layout.shrink()),

    Key("M-<period>", lazy.layout.toggle_split()),

    Key("M-<grave>", rot_layout()),
    Key("M-A-<grave>", rot_layout(-1)),
    Key("M-<Tab>", lazy.screen.toggle_group()),
    Key("M-S-q", lazy.window.kill()),

    Key("M-A-r", lazy.restart()),
    Key("M-A-q", lazy.shutdown()),
    Key("M-r", lazy.spawncmd()),
    
    Key("M-<Return>", lazy.spawn("xterm")),
    Key("M-w", lazy.spawn("rofi -show window")),
    Key("M-s", lazy.spawn("rofi -show run")),
    Key("M-A-l", lazy.spawn("xscreensaver-command -lock")),
    
    Key("M-z", lazy.spawn("spotify")),
    Key("M-x", lazy.spawn("chromium")),
    Key("M-c", lazy.spawn("gimp")),
    Key("M-v", lazy.spawn("gedit")),
    Key("M-b", lazy.spawn("pcmanfm"))
]


#group initialization

groups = [Group(i) for i in "1234567890"] 

for g in groups:
    keys.extend([
        
        Key("M-%d" % int(g.name), focus_or_switch(g.name)),
        Key("M-S-%d" % int(g.name), lazy.window.togroup(g.name))

    ])

#layouts

LAYOUT_PARAMS = { 
    'border_normal' : GRAY,
    'border_focus' : WHITE,
    'border_width' : 2,
    'margin' : 7
}

layouts = [
    layout.Max(),
    layout.Stack(num_stacks=2, **LAYOUT_PARAMS),
    layout.VerticalTile(**LAYOUT_PARAMS),
    layout.Bsp(**LAYOUT_PARAMS),
    layout.TreeTab(),
    layout.MonadTall(**LAYOUT_PARAMS),
    layout.MonadWide(**LAYOUT_PARAMS)
]

widget_defaults = dict(
    font = 'Sans',
    fontsize = 12,
    padding = 3
)

extension_defaults = widget_defaults.copy()


#bar initialization

main_bar = bar.Bar(
    [
        widget.GroupBox(background=GRAY,
            highlight_method = "block",
            urgent_border = SECONDARY,
            inactive = BLACK,
            disable_drag = True,
            other_current_screen_border = TERTIARY,
            this_current_screen_border = PRIMARY,
            other_screen_border = BLACK,
            this_screen_border = BLACK,
            highlight_color = TERTIARY
            ),
        _separator(GRAY, PRIMARY),
        widget.CurrentLayout(background=PRIMARY),
        _separator(PRIMARY, BLACK),
        widget.TaskList(background=BLACK,
            highlight_method="block",
            border=GRAY,
            title_width_method = 'uniform',
            urgent_border = SECONDARY,
            unfocused_border = GRAY,
            max_title_width = 300
        ),
        widget.Sep(foreground=BLACK, background=BLACK),
        _separator(GRAY, BLACK, "left"),
        widget.CPUGraph(
            background=GRAY, 
            type="line", 
            line_width=1, 
            border_width=2, 
            border_color=PRIMARY, 
            graph_color=PRIMARY, 
            width=50),
        widget.MemoryGraph(
            background=GRAY,
            type="line", 
            line_width=1, 
            border_width=2, 
            border_color=TERTIARY, 
            graph_color=TERTIARY, 
            width=50),
        widget.NetGraph(
            background=GRAY,
            type="line", 
            line_width=1, 
            border_width=2, 
            border_color=SECONDARY, 
            graph_color=SECONDARY, 
            width=50
	),
	widget.Clock(format="%Y-%m-%d %a %I:%M %p", background=GRAY),
        _separator(TERTIARY, GRAY, "left"),
        widget.Systray(background=TERTIARY),
        _separator(SECONDARY, TERTIARY, "left"),
        widget.Prompt(background=SECONDARY),
    ],
    24,
    background=BLACK
)

def make_screen():
    secondary_bar = bar.Bar(
        [
            widget.GroupBox(background=GRAY,
                highlight_method = "block",
                urgent_border = SECONDARY,
                inactive = BLACK,
                disable_drag = True,
                other_current_screen_border = TERTIARY,
                this_current_screen_border = PRIMARY,
                other_screen_border = BLACK,
                this_screen_border = BLACK,
                highlight_color = TERTIARY
            ),
            _separator(GRAY, BLACK),
            widget.TaskList(background=BLACK,
                highlight_method="block",
                border=GRAY,
                title_width_method = 'uniform',
                urgent_border = SECONDARY,
                unfocused_border = GRAY,
                max_title_width = 300
            ),
            _separator(PRIMARY, BLACK, "left"),
            widget.CurrentLayoutIcon(background=PRIMARY)
        ],
        24,
        background=BLACK
    )

    return Screen(bottom=secondary_bar)


screens = [
    Screen(bottom=main_bar),
    make_screen()
]


#mouse for floating layout

mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]

#floating rules for better window placement

floating_layout = layout.Floating(**LAYOUT_PARAMS, float_rules = [
    { 'wmclass': 'confirm'},
    { 'wmclass': 'dialog'},
    { 'wmclass': 'download'},
    { 'wmclass': 'error'},
    { 'wmclass': 'file_progress'},
    { 'wmclass': 'notification'},
    { 'wmclass': 'splash'},
    { 'wmclass': 'toolbar'},
    { 'wmclass': 'confirmreset'},
    { 'wmclass': 'makebranch'},
    { 'wmclass': 'maketag'},
    { 'wname': 'branchdialog'},
    { 'wname': 'pinentry'},
    { 'wmclass': 'ssh-askpass'}
])

#rules

dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = False
cursor_warp = True 
auto_fullscreen = True
focus_on_window_activation = 'smart'
wmname = "LG3D"
main = None
