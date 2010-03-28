#!/usr/bin/env python
#
# Ross Burton <ross@burtonini.com>
# Dafydd Harries <daf@rhydd.org>
#
# PyGTK Version by:
#  Thomas Wood <thos@gnome.org>
#
# Copyright 2009 Intel Corporation
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

import os
import gtk
import re
import sys

import turbine.template

PACKAGE_NAME    = "GObject Generator"
PACKAGE_VERSION = "0.1"
PACKAGE_AUTHORS = ["Thomas Wood <thos@gnome.org>",
                   "Ross Burton <ross@burtonini.com>",
                   "Dafydd Harries <daf@rhydd.org>"]
PACKAGE_COPYRIGHT = "Copyright 2009 Intel Corporation\n" \
                    "Copyright 2005 Ross Burton, Dafydd Harries"

def make_iface_init_func_name (iface):
    return (iface.replace ('_TYPE', '') + '_iface_init').lower()

def make_indent (str):
    result = ""
    while (len (str) > len (result)):
        result += ' '
    return result

def make_type_definition (data):
    define_type = ''
    define_extra = ''

    if (len (data['interfaces']) > 0):

        if (data['abstract']):
            define_macro = "G_DEFINE_ABSTRACT_TYPE_WITH_CODE";
        else:
            define_macro = "G_DEFINE_TYPE_WITH_CODE"

        define_extra = "\n"
        for row in data['interfaces']:
            define_type += "static void " + make_iface_init_func_name (row[0]) \
                           + " (" + row[1] + " *iface);\n"
            define_extra += "static void\n" \
                            + make_iface_init_func_name (row[0]) \
                            + " (" + row[1] + " *iface)\n" \
                            + "{\n\n}\n\n";
        define_type += "\n" + define_macro + " ("+ data['class_camel'] \
                       + ", " \
                       + data['class_lower'] + ", " + data['parent'] + ","
        for row in data['interfaces']:
            iface = row[0]
            define_type = define_type + '\n' + make_indent (define_macro) + \
                          "  G_IMPLEMENT_INTERFACE (" + iface + ', ' + \
                           make_iface_init_func_name (iface) + ')'
        define_type += ')'
    else:
        if (data['abstract']):
            define_macro = "G_DEFINE_ABSTRACT_TYPE"
        else:
            define_macro = "G_DEFINE_TYPE"
        define_type = define_macro + " ("+ data['class_camel'] + ", " \
                      + data['class_lower'] + ", " + data['parent'] + ')'

    return (define_type, define_extra)


def make_class_init(data):
    lines = [
        'static void',
        '%(class_lower)s_class_init (%(class_camel)sClass *klass)',
        '{'
        ]

    if data['dispose'] or data['finalize'] or data['private']:
        lines.append('  GObjectClass *object_class = G_OBJECT_CLASS (klass);')
        lines.append('')

    if data['private']:
        lines.append(
            '  g_type_class_add_private (klass, '
            'sizeof (%(class_camel)sPrivate));')

    if data['dispose'] or data['finalize'] or data['props']:
        lines.append('')

    if data['props']:
        lines.append('  object_class->get_property = %(class_lower)s_get_property;')
        lines.append('  object_class->set_property = %(class_lower)s_set_property;')

    if data['dispose']:
        lines.append('  object_class->dispose = %(class_lower)s_dispose;')

    if data['finalize']:
        lines.append('  object_class->finalize = %(class_lower)s_finalize;')

    lines.append('}')
    return ''.join([line % data + '\n' for line in lines])

def handle_post(button, ui):
    string_keys = ("class_camel", "class_lower", "package_upper",
                   "object_upper", "parent", "parent_camel");
    bool_keys = ("props", "finalize", "dispose", "private", "abstract");
    data = {}

    model = ui.get_object ('interfaces-model')
    i = 0
    data['interfaces'] = model

    for key in string_keys:
        # TODO: sanity check against nulls
        data[key] = ui.get_object (key).get_text()

    for key in bool_keys:
        data[key] = ui.get_object (key).get_active()

    if (data['class_lower'] == ''):
      dlg = gtk.MessageDialog (ui.get_object ("main-window"), gtk.DIALOG_MODAL,
                               gtk.MESSAGE_ERROR, gtk.BUTTONS_OK)
      dlg.set_markup ("No class name specified!")
      dlg.run ()
      dlg.destroy ()
      return

    data['filename'] = data['class_lower'].replace('_', "-")
    data['class_init'] = make_class_init(data).strip()
    (data['define_type'], data['interface_init']) = make_type_definition (data)
    data['header_guard'] = "_" + data['filename'].upper().replace('.', '_').replace('-', '_') + "_H"
    extra = []
    private = []

    if data['private']:
        private.append(template.private_template)
        data['priv_init'] = "  self->priv = " + data['object_upper'] + "_PRIVATE (self);"
        data['priv_member'] = "  " + data['class_camel'] + "Private *priv;"
        data['priv_typedef'] = "typedef struct _" + data['class_camel'] + "Private " + data['class_camel'] + "Private;"
    else:
        data['priv_init'] = "";
        data['priv_member'] = "";
        data['priv_typedef'] = "";

    if data['props']:
        indent = {}
        indent['class_lower'] = data['class_lower']
        indent['function_len'] = " " * (len(data['class_lower']) + 13)
        extra.append(template.prop_template % indent)

    if data['dispose']:
        extra.append(template.dispose_template)

    if data['finalize']:
        extra.append(template.finalize_template)

    data['private'] = '\n'.join([x % data for x in private])

    data['extra'] = '\n'.join([x % data for x in extra])

    select_folder = gtk.FileChooserDialog(title="Select Destination",
                                    action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                    buttons=(gtk.STOCK_CANCEL,
                                    gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OPEN,
                                    gtk.RESPONSE_ACCEPT))
    if select_folder.run() == gtk.RESPONSE_ACCEPT:
        folder = select_folder.get_filename() + "/"
    else:
        folder = ""
    select_folder.destroy()
    if folder == "":
        return

    f = open (folder + data['filename'] + '.h', 'w')
    f.write (template.h_template % data)

    f = open (folder + data['filename'] + '.c', 'w')
    f.write (template.c_template % data)

    s = ui.get_object ('statusbar')
    s.push (0, 'Object saved as "' + data['filename'] + '.{c,h}"')

def guess_class_params (entry, ui):

    text = entry.get_text()
    m = re.findall ('[A-Z]+[a-z0-9]*', text)
    if (m):
      s = m[0]
    else:
      s = ''
    ui.get_object ('package_upper').set_text (s.upper())

    if (m and len(m) > 1):
      s = m[1]
      i = 2
      while (i < len(m)):
        s = s + "_" + m[i]
        i = i + 1
    else:
       s = ''

    ui.get_object ('object_upper').set_text (s.upper())

    if (m):
      s = m[0]
      i = 1
      while (i < len(m)):
        s = s + "_" + m[i]
        i = i + 1
    else:
      s = ''

    ui.get_object ('class_lower').set_text (s.lower())

    ui.get_object ('save-button').set_sensitive ((text != "") and (ui.get_object ('parent_camel').get_text () != ""))

def guess_parent_params (entry, ui):

    text = entry.get_text()

    # special case GObject
    s = ''
    prefix = re.match ('[A-Z][a-z]*', text)
    if (prefix):
      prefix = prefix.group (0)
      text = text.replace (prefix, '', 1)
      m = re.findall ('[A-Z]+[a-z]*', text)
      s = prefix + '_TYPE'
      if (m):
        for i in m:
          s = s + "_" + i

    ui.get_object ('parent').set_text (s.upper())

    ui.get_object ('save-button').set_sensitive ((text != "") and (ui.get_object ('class_camel').get_text () != ""))


def about_button_clicked_cb (button, ui):
    about = gtk.AboutDialog()
    about.set_transient_for (ui.get_object ('main-window'))
    about.set_name (PACKAGE_NAME)
    about.set_version (PACKAGE_VERSION)
    about.set_authors (PACKAGE_AUTHORS)
    about.set_copyright (PACKAGE_COPYRIGHT);
    about.set_license ("""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
                       """)
    about.set_comments ("Generates GObjects from the given parameters")
    about.set_logo_icon_name ("applications-development")
    about.run ()
    about.destroy ()

def add_interface_cb (button, ui):
    model = ui.get_object ("interfaces-model")
    iter = model.append (["", ""])
    treeview = ui.get_object ("interfaces-treeview")

    column = treeview.get_column (0)
    path = model.get_path (iter)

    treeview.set_cursor (path, column, True)

def remove_interface_cb (button, ui):
    selection = ui.get_object ("interfaces-treeview").get_selection ()
    (model, iter) = selection.get_selected ()
    if (iter == None):
        return
    # move selection forward
    newiter = model.iter_next (iter)
    # or backward ...
    if (newiter == None):
        path = model.get_path (iter)
        path = (path[0] - 1,)
        if (path[0] >= 0):
          newiter = model.get_iter (path)

    if (newiter):
      selection.select_iter (newiter)
    if (iter):
        model.remove (iter);

def interface_edited_cb (cellrenderertext, path, new_text, ui):
    model = ui.get_object ("interfaces-model")
    iter = model.get_iter (path)
    struct_name = new_text.replace ('_TYPE', '').replace ('_', ' ').title().replace (' ', '') + 'Iface';
    model.set (model.get_iter (path), 0, new_text, 1, struct_name)

def clear_ui (button, ui):
    entry = ui.get_object
    string_keys = ("class_camel", "class_lower", "package_upper",
                   "object_upper", "parent", "parent_camel");
    for key in string_keys:
        ui.get_object (key).set_text ("")
    model = ui.get_object ('interfaces-model').clear ()

def entry_focus_in_cb (entry, event, ui):
    ui.get_object ("statusbar").push (0, entry.get_tooltip_text ())

def entry_focus_out_cb (entry, event, ui):
    ui.get_object ("statusbar").pop (0)

def main(argv = sys.argv, stdout=sys.stdout, stderr=sys.stderr):
    ui = gtk.Builder()
    ui_file = os.path.join(os.path.dirname(__file__), 'turbine.xml');
    ui.add_from_file (ui_file)

    window = ui.get_object ('main-window')
    window.show_all()
    window.connect ('delete-event', gtk.main_quit);

    button = ui.get_object ('new-button')
    button.connect ('clicked', clear_ui, ui)

    button = ui.get_object ('save-button')
    button.connect ('clicked', handle_post, ui)

    button = ui.get_object ('about-button')
    button.connect ('clicked', about_button_clicked_cb, ui)

    # enable hint text in the status bar
    string_keys = ("class_camel", "class_lower", "package_upper",
                   "object_upper", "parent", "parent_camel");
    for key in string_keys:
        ui.get_object (key).connect ("focus-in-event", entry_focus_in_cb, ui)
        ui.get_object (key).connect ("focus-out-event", entry_focus_out_cb, ui)

    ui.get_object ('class_camel').connect ('changed', guess_class_params, ui)
    ui.get_object ('parent_camel').connect ('changed', guess_parent_params, ui)

    # implemented interfaces
    ui.get_object ('add-interface-button').connect ('clicked',
                                                    add_interface_cb, ui)
    ui.get_object ('remove-interface-button').connect ('clicked',
                                                       remove_interface_cb, ui)
    ui.get_object ('interfaces-treeviewcell').connect ('edited',
                                                       interface_edited_cb, ui)

    gtk.main()

