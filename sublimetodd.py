import configparser
import sublime

from datetime import datetime

from sublime_plugin import WindowCommand, TextCommand


TODD_TPL = """\
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
    {notes}


# Movement:
#    r = refresh
#
# Operations:
#    s = Complete task
#    a = Add new task
#    n = Add new note

Last Refreshed - {updated}
"""


def get_tasks(path):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(path)
    return config


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
        
        tasks = get_tasks('sublime-todd/tasks.ini')
        
        context = {
            'todos': "\n\t".join([x for x in tasks['todos']]),
            'doings': "\n\t".join([x for x in tasks['doings']]),
            'dones': "\n\t".join([x for x in tasks['dones']]),
            'notes': "\n\t".join([x for x in tasks['notes']]),
            'updated': datetime.now()
        }

        output = TODD_TPL.format(**context)

        self.view.replace(edit, sublime.Region(0, self.view.size()), output)
        self.view.set_read_only(True)

        # By default the entire buffer is selected, clear the selection and
        # move the cursor to the top line
        self.view.sel().clear()
        self.view.set_viewport_position((0.0, 0.0), False)
        self.view.sel().add(sublime.Region(0))
