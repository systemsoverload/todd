import sublime
import toml

from datetime import datetime

from sublime_plugin import WindowCommand, TextCommand, EventListener, TextInputHandler


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

class Tasks:
    def __init__(self, task_data_path):
        self.task_data = toml.load(open(task_data_path))

    @property
    def overview(self):
        return {
            'todos': "\n    ".join([x['title'] for x in self.task_data['todos']]),
            'doings': "\n    ".join([x['title'] for x in self.task_data['doings']]),
            'dones': "\n    ".join([x['title'] for x in self.task_data['dones']]),
            'notes': "\n    ".join([x['title'] for x in self.task_data['notes']]),
            'updated': datetime.now()
        }

    def add(self, title):
        self.task_data['todos'].append({"title": title, "created_on": datetime.now()})

    def _write(self):
        print("STUB - write task_data back to file here")

def get_tasks() -> Tasks:
    tasks = Tasks("tasks.toml")

    return tasks


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
            view.set_name("Todd")
            view.set_scratch(True)
            view.settings().set('todd_view', 'status')
            view.settings().set('word_wrap', False)
            view.assign_syntax('Packages/sublime-todd/sublimetodd-status.sublime-syntax')
            view.run_command('todd_status_refresh')

        self.window.focus_view(view)



class ToddStatusRefreshCommand(TextCommand):
    def run(self, edit):
        print("Todd status refreshed...")
        self.view.set_read_only(False)

        self.view.tasks = get_tasks()

        output = TODD_TPL.format(**self.view.tasks.overview)

        self.view.replace(edit, sublime.Region(0, self.view.size()), output)
        self.view.set_read_only(True)

        # By default the entire buffer is selected, clear the selection and
        # move the cursor to the top line
        self.view.sel().clear()
        self.view.set_viewport_position((0.0, 0.0), False)
        self.view.sel().add(sublime.Region(238, 238))


class ToddStatusCompleteTaskCommand(TextCommand):
    def run(self, edit):
        print("STUB - Complete this task")


class ToddStatusAddTaskCommand(TextCommand):
    def run(self, edit):
        print("STUB - add a new task")
        ToddAddTaskInputHandler(self.view)


class ToddAddTaskInputHandler(TextInputHandler):
    def __init__(self, view):
        self.view = view

    def placeholder(self):
        return "Hello"


def remove_context_phantoms(view):
    existing_pid = view.settings().get('context_phantom_pid')
    if existing_pid:
        view.erase_phantom_by_id(existing_pid)

        return True
    return False


class ToddStatusExpandContext(TextCommand):
    def run(self, edit):
        # Never allow more than one context expansion
        remove_context_phantoms(self.view)
        cur_line_text = self.view.substr(self.view.line(self.view.sel()[0])).lstrip()
        cur_task = None
        for task_type, tasks in self.view.tasks.task_data.items():
            for task in tasks:
                if task['title']==cur_line_text:
                    cur_task = task

        if cur_task:
            message = """<body>
                           <style>
                             body{{
                               padding: 40px;
                               background-color: color(var(--background) alpha(0.25));
                             }}
                             .item{{
                               margin-bottom: 12px;
                             }}
                           </style>
                           <div class="item">{}</div>
                           <div class="item">created on {}</div>
                          </body>""".format(cur_task.get('details', ''), cur_task['created_on'])
            pid = self.view.add_phantom("test", self.view.sel()[-1], message, sublime.LAYOUT_BLOCK)
            self.view.settings().set('context_phantom_pid', pid)


class ToddEventListeners(EventListener):

    # def on_selection_modified(self, view):
    #     """Automatically collapse context details when moving cursor"""
    #     # Ignore hook for non-todd views
    #     if view.settings().get('todd_view'):
    #         remove_context_phantoms(view)
    #         # TODO - auto-expand the context of the next target line if valid?
    #         #print(view.scope_name(view.sel()[-1].b))

    def on_activated(self, view):
        # Ignore hook for non-todd views
        if view.settings().get('todd_view'):
            view.run_command('todd_status_refresh')
