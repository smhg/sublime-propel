import os
import sublime
import sublime_plugin
from asyncprocess import *

RESULT_VIEW_NAME = 'propel_result'

class PropelGenerateCommand(sublime_plugin.WindowCommand):
  def run(self, action=None):
    dir_name = os.path.dirname(self.window.active_view().file_name())
    self.buffered_data = ''
    self.dir_name = dir_name
    self.is_running = True
    self.tests_panel_showed = False
    self.init_tests_panel()
    cmd = "propel-gen"
    if action:
      cmd = cmd + " " + action
    AsyncProcess(dir_name, cmd, self)

  def init_tests_panel(self):
    if not hasattr(self, 'output_view'):
      self.output_view = self.window.get_output_panel(RESULT_VIEW_NAME)
      self.output_view.set_name(RESULT_VIEW_NAME)
    self.clear_test_view()
    self.output_view.settings().set("dir_name", self.dir_name)

  def show_tests_panel(self):
    if self.tests_panel_showed:
      return
    self.window.run_command("show_panel", {"panel": "output." + RESULT_VIEW_NAME})
    self.tests_panel_showed = True

  def clear_test_view(self):
    self.output_view.set_read_only(False)
    edit = self.output_view.begin_edit()
    self.output_view.erase(edit, sublime.Region(0, self.output_view.size()))
    self.output_view.end_edit(edit)
    self.output_view.set_read_only(True)

  def append_data(self, proc, data, end=False):
    self.buffered_data = self.buffered_data + data.decode("utf-8")
    print self.buffered_data
    data = self.buffered_data.replace('\r\n', '\n').replace('\r', '\n')

    if end == False:
      rsep_pos = data.rfind('\n')
      if rsep_pos == -1:
        # not found full line.
        return
      self.buffered_data = data[rsep_pos+1:]
      data = data[:rsep_pos+1]

    # ignore error.
    text = data

    self.show_tests_panel()
    selection_was_at_end = (len(self.output_view.sel()) == 1 and self.output_view.sel()[0] == sublime.Region(self.output_view.size()))
    self.output_view.set_read_only(False)
    edit = self.output_view.begin_edit()
    self.output_view.insert(edit, self.output_view.size(), text)
    self.output_view.show(self.output_view.size())

    self.output_view.end_edit(edit)
    self.output_view.set_read_only(True)

  def proc_terminated(self, proc):
    return