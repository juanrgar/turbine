# Ross Burton <ross@burtonini.com>
# Dafydd Harries <daf@rhydd.org>
#
# PyGTK Version by:
#  Thomas Wood <thos@gnome.org>
#
# Copyright 2009,2010,2012 Intel Corporation
# Copyright 2005 Ross Burton
# Copyright 2005 Dafydd Harries
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Template text is Public Domain

from gi.repository import GLib, Gtk, Gio
from gettext import gettext as _
import os

from turbine.window import Window
from turbine.controller import Controller

class Application (Gtk.Application):

    def __init__ (self):
        Gtk.Application.__init__(self, application_id='org.gnome.Turbine', flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_application_name(_('Turbine'))

        self._window = None
        self._controller = None

    def do_startup (self):
        Gtk.Application.do_startup (self)
        self.build_app_menu ()
        self._controller = Controller ()

    def build_app_menu (self):
        builder = Gtk.Builder()
        ui_file = os.path.join(os.path.dirname(__file__), 'app_menu.ui');
        builder.add_from_file (ui_file)

        self.set_app_menu (builder.get_object ('app-menu'))

        about_action = Gio.SimpleAction.new ('about', None)
        about_action.connect ('activate', self.about)
        self.add_action (about_action)

        quit_action = Gio.SimpleAction.new ('quit', None)
        quit_action.connect ('activate', self.quit)
        self.add_action (quit_action)

    def about (self, action, param):
        builder = Gtk.Builder ()
        ui_file = os.path.join (os.path.dirname(__file__), 'about_dialog.ui')
        builder.add_from_file (ui_file)

        about_dialog = builder.get_object ('about_dialog')
        about_dialog.set_transient_for (self._window)
        about_dialog.connect ('response', self.about_response)
        about_dialog.show ()

    def about_response (self, dialog, response):
        dialog.destroy ()

    def quit (self, action, param):
        self._window.destroy()

    def do_activate (self):
        if not self._window:
            self._window = Window (self)
            self._window.set_controller (self._controller)
        self._window.present()

