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

from turbine import template

import re

class Controller:

    def __init__ (self):
        pass

    def save (self, folder, data):
        data['filename'] = data['class-lower'].replace('_', '-')
        data['class-init'] = self.make_class_init(data).strip()
        (data['define-type'], data['interface-init']) = self.make_type_definition (data)
        data['header-guard'] = '__' + data['filename'].upper().replace('.', '_').replace('-', '_') + '_H__'
        extra = []
        private = []

        if data['private']:
            private.append(template.private_template)
            data['priv-init'] = "  self->priv = " + data['object-upper'] + "_PRIVATE (self);"
            data['priv-member'] = "  " + data['class-camel'] + "Private *priv;"
            data['priv-typedef'] = "typedef struct _" + data['class-camel'] + "Private " + data['class-camel'] + "Private;"
        else:
            data['priv-init'] = "";
            data['priv-member'] = "";
            data['priv-typedef'] = "";

        if data['props']:
            indent = {}
            indent['class-lower'] = data['class-lower']
            indent['function-len'] = " " * (len(data['class-lower']) + 13)
            extra.append(template.prop_template % indent)

        if data['dispose']:
            extra.append(template.dispose_template)

        if data['finalize']:
            extra.append(template.finalize_template)

        data['private'] = '\n'.join([x % data for x in private])

        data['extra'] = '\n'.join([x % data for x in extra])

        f = open (folder + data['filename'] + '.h', 'w')
        f.write (template.h_template % data)

        f = open (folder + data['filename'] + '.c', 'w')
        f.write (template.c_template % data)

        return (True, data['filename'])

    def make_class_init (self, data):
        lines = [
            'static void',
            '%(class-lower)s_class_init (%(class-camel)sClass *klass)',
            '{'
            ]
    
        if data['dispose'] or data['finalize'] or data['private']:
            lines.append('  GObjectClass *object_class = G_OBJECT_CLASS (klass);')
            lines.append('')
    
        if data['private']:
            lines.append(
                '  g_type_class_add_private (klass, '
                'sizeof (%(class-camel)sPrivate));')
    
        if data['dispose'] or data['finalize'] or data['props']:
            lines.append('')
    
        if data['props']:
            lines.append('  object_class->get_property = %(class-lower)s_get_property;')
            lines.append('  object_class->set_property = %(class-lower)s_set_property;')
    
        if data['dispose']:
            lines.append('  object_class->dispose = %(class-lower)s_dispose;')
    
        if data['finalize']:
            lines.append('  object_class->finalize = %(class-lower)s_finalize;')
    
        lines.append('}')
        return ''.join([line % data + '\n' for line in lines])

    def make_iface_init_func_name (self, iface):
        return (iface.replace ('_TYPE', '') + '_iface_init').lower()
    
    def make_indent (str):
        result = ""
        while (len (str) > len (result)):
            result += ' '
        return result
    
    def make_type_definition (self, data):
        define_type = ''
        define_extra = ''
    
        if (len (data['interfaces']) > 0):
    
            if (data['abstract']):
                define_macro = "G_DEFINE_ABSTRACT_TYPE_WITH_CODE";
            else:
                define_macro = "G_DEFINE_TYPE_WITH_CODE"
    
            define_extra = "\n"
            for row in data['interfaces']:
                define_type += "static void " + self.make_iface_init_func_name (row[0]) \
                               + " (" + row[1] + " *iface);\n"
                define_extra += "static void\n" \
                                + self.make_iface_init_func_name (row[0]) \
                                + " (" + row[1] + " *iface)\n" \
                                + "{\n\n}\n\n";
            define_type += "\n" + define_macro + " ("+ data['class-camel'] \
                           + ", " \
                           + data['class-lower'] + ", " + data['parent'] + ","
            for row in data['interfaces']:
                iface = row[0]
                define_type = define_type + '\n' + self.make_indent (define_macro) + \
                              "  G_IMPLEMENT_INTERFACE (" + iface + ', ' + \
                               self.make_iface_init_func_name (iface) + ')'
            define_type += ')'
        else:
            if (data['abstract']):
                define_macro = "G_DEFINE_ABSTRACT_TYPE"
            else:
                define_macro = "G_DEFINE_TYPE"
            define_type = define_macro + " ("+ data['class-camel'] + ", " \
                          + data['class-lower'] + ", " + data['parent'] + ')'
    
        return (define_type, define_extra)

