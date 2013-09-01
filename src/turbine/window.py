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

from gi.repository import Gtk, Gio
from gettext import gettext as _

import os
import re

class Window (Gtk.ApplicationWindow):

    def __init__ (self, app):
        Gtk.ApplicationWindow.__init__ (self, application=app, title=_('Turbine'))
        self._builder = None

        self.setup_view ()
        self.set_size_request (400, 600)
        self.set_icon_name ('applications-development')

    def setup_view (self):
        self._builder = Gtk.Builder ()
        ui_file = os.path.join (os.path.dirname(__file__), 'window.ui')
        self._builder.add_from_file (ui_file)

        headerbar = self._builder.get_object ('headerbar')
        main_vbox = self._builder.get_object ('main_vbox')
        new_button = self._builder.get_object ('new_button')
        save_button = self._builder.get_object ('save_button')
        class_camel_entry = self._builder.get_object ('class_camel')
        parent_camel_entry = self._builder.get_object ('parent_camel')
        add_interface_button = self._builder.get_object ('add-interface-button')
        remove_interface_button = self._builder.get_object ('remove-interface-button')
        interfaces_treeviewcell = self._builder.get_object ('interfaces_treeviewcell')

        new_button.connect ('clicked', self.new)
        save_button.connect ('clicked', self.save)
        class_camel_entry.connect ('changed', self.guess_class_params)
        parent_camel_entry.connect ('changed', self.guess_parent_params)
        add_interface_button.connect ('clicked', self.add_interface)
        remove_interface_button.connect ('clicked', self.remove_interface)
        interfaces_treeviewcell.connect ('edited', self.interface_edited)

        self.setup_statusbar ()

        self.set_titlebar (headerbar)
        self.add (main_vbox)
        self.show_all ()

    def new (self, widget):
        string_keys = ('class_camel', 'class_lower', 'package_upper',
                       'object_upper', 'parent', 'parent_camel')
        for key in string_keys:
            self._builder.get_object (key).set_text ('')
        self._builder.get_object ('interfaces_model').clear ()

    def save (self, widget):
        select_folder = Gtk.FileChooserDialog('Select Destination',
                                              self,
                                              Gtk.FileChooserAction.SELECT_FOLDER,
                                              (Gtk.STOCK_CANCEL,
                                               Gtk.ResponseType.CANCEL,
                                               Gtk.STOCK_OPEN,
                                               Gtk.ResponseType.ACCEPT))
        if select_folder.run() == Gtk.ResponseType.ACCEPT:
            folder = select_folder.get_filename() + '/'
        else:
            folder = ''
        select_folder.destroy()
        if folder == '':
            return

        string_keys = ('class_camel', 'class_lower', 'package_upper',
                       'object_upper', 'parent', 'parent_camel')
        bool_keys = ('props', 'finalize', 'dispose', 'private', 'abstract')
        data = {}

        model = self._builder.get_object ('interfaces_model')
        data['interfaces'] = model

        for key in string_keys:
            # TODO: sanity check against nulls
            data[key] = self._builder.get_object (key).get_text()

        for key in bool_keys:
            data[key] = self._builder.get_object (key).get_active()

#        if data['class_lower'] == '':
#          dlg = Gtk.MessageDialog (self._builder.get_object ('main-window'), Gtk.DIALOG_MODAL,
#                                   Gtk.MESSAGE_ERROR, Gtk.BUTTONS_OK)
#          dlg.set_markup ("No class name specified!")
#          dlg.run ()
#          dlg.destroy ()
#          return

        (succ, filename) = self._controller.save (folder, data)

        if succ:
            s = self._builder.get_object ('statusbar')
            s.push (0, 'Object saved as "' + filename + '.{c,h}"')

    def setup_statusbar (self):
        string_keys = ('class_camel', 'class_lower', 'package_upper',
                       'object_upper', 'parent', 'parent_camel')
        for key in string_keys:
            self._builder.get_object (key).connect ('focus-in-event', self.entry_focus_in)
            self._builder.get_object (key).connect ('focus-out-event', self.entry_focus_out)

    def entry_focus_in (self, entry, event):
        self._builder.get_object ('statusbar').push (0, entry.get_tooltip_text ())

    def entry_focus_out (self, entry, event):
        self._builder.get_object ('statusbar').pop (0)

    def guess_class_params (self, entry):
        text = entry.get_text()
        m = re.findall ('[A-Z]+[a-z0-9]*', text)
        if (m):
          s = m[0]
        else:
          s = ''
        self._builder.get_object ('package_upper').set_text (s.upper())

        if (m and len(m) > 1):
          s = m[1]
          i = 2
          while (i < len(m)):
            s = s + '_' + m[i]
            i = i + 1
        else:
           s = ''

        self._builder.get_object ('object_upper').set_text (s.upper())

        if (m):
          s = m[0]
          i = 1
          while (i < len(m)):
            s = s + '_' + m[i]
            i = i + 1
        else:
          s = ''

        self._builder.get_object ('class_lower').set_text (s.lower())

        self._builder.get_object ('save_button').set_sensitive ((text != '') and (self._builder.get_object ('parent_camel').get_text () != ''))

    def guess_parent_params (self, entry):
        text = entry.get_text()

        # special case GObject
        s = ''
        prefix = re.match ('[A-Z][a-z]*', text)
        if prefix:
          prefix = prefix.group (0)
          text = text.replace (prefix, '', 1)
          m = re.findall ('[A-Z]+[a-z]*', text)
          s = prefix + '_TYPE'
          if m:
            for i in m:
              s = s + '_' + i

        self._builder.get_object ('parent').set_text (s.upper())

        self._builder.get_object ('save_button').set_sensitive ((text != '') and (self._builder.get_object ('class_camel').get_text () != ''))

    def add_interface (self, widget):
        model = self._builder.get_object ('interfaces_model')
        iter = model.append (['', ''])
        treeview = self._builder.get_object ('interfaces_treeview')
        column = treeview.get_column (0)
        path = model.get_path (iter)
        treeview.set_cursor (path, column, True)

    def remove_interface (self, widget):
        selection = self._builder.get_object ('interfaces_treeview').get_selection ()
        (model, iter) = selection.get_selected ()
        if iter == None:
            return
        # move selection forward
        newiter = model.iter_next (iter)
        # or backward ...
        if newiter == None:
            path = model.get_path (iter)
            path = (path[0] - 1,)
            if (path[0] >= 0):
              newiter = model.get_iter (path)

        if newiter:
          selection.select_iter (newiter)
        if iter:
            model.remove (iter)

    def interface_edited (self, renderer, path, new_text):
        model = self._builder.get_object ('interfaces_model')
        iter = model.get_iter (path)
        struct_name = new_text.replace ('_TYPE', '').replace ('_', ' ').title().replace (' ', '') + 'Iface'
        model.set (model.get_iter (path), 0, new_text, 1, struct_name)

    def set_controller (self, controller):
        self._controller = controller

