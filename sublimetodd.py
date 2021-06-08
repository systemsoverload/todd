import sublime
from sublime_plugin import WindowCommand, TextCommand


TODD_HELP = """\
▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉
▉▉                     Hi, I'm Todd                     ▉▉
▉▉                                                      ▉▉
▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉


To-do:
    {todos}

Doing:
    {doings}

Done:
    {dones}

Notes:
    Long lived reminder; call your mother


# Movement:
#    r = refresh
#
# Operations:
#    s = Complete task
#    a = Add new task
#    n = Add new note

Last Refreshed - {}
"""
['Create sublimetext plugin for managing']
['Decide on a name for sublimetext task management plugin']
['Create simple storage backend for tasks']

def find_view_by_settings(window, **kwargs):
    for view in window.views():
        s = view.settings()
        matches = [s.get(k) == v for k, v in list(kwargs.items())]

        if all(matches):
            return view


class ToddStatusCommand(WindowCommand):
    def run(self):
        view = find_view_by_settings(self.window, todd_view='status')

        if not view:
            view = self.window.new_file()
            view.set_name("todd")
            view.set_scratch(True)
            view.settings().set('todd_view', 'status')
            view.settings().set('word_wrap', False)
            view.assign_syntax('Packages/sublime-todd/sublimetodd-status.sublime-syntax')

        view.run_command('todd_status_refresh')
        self.window.focus_view(view)



class ToddStatusRefreshCommand(TextCommand):
    def run(self, edit):
        self.view.set_read_only(False)
        # XXX - Actual data fetch should go here
        from datetime import datetime
        self.view.replace(edit, sublime.Region(0, self.view.size()), TODD_HELP.format(datetime.now()))
        self.view.set_read_only(True)

        # By default the entire buffer is selected, clear the selection and
        # move the cursor to the top line
        self.view.sel().clear()
        self.view.set_viewport_position((0.0, 0.0), False)
        self.view.sel().add(sublime.Region(0))
