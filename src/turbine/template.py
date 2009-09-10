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

h_template = """\
/* %(filename)s.h */

#ifndef %(header_guard)s
#define %(header_guard)s

#include <glib-object.h>

G_BEGIN_DECLS

#define %(package_upper)s_TYPE_%(object_upper)s %(class_lower)s_get_type()

#define %(package_upper)s_%(object_upper)s(obj) \\
  (G_TYPE_CHECK_INSTANCE_CAST ((obj), \\
  %(package_upper)s_TYPE_%(object_upper)s, %(class_camel)s))

#define %(package_upper)s_%(object_upper)s_CLASS(klass) \\
  (G_TYPE_CHECK_CLASS_CAST ((klass), \\
  %(package_upper)s_TYPE_%(object_upper)s, %(class_camel)sClass))

#define %(package_upper)s_IS_%(object_upper)s(obj) \\
  (G_TYPE_CHECK_INSTANCE_TYPE ((obj), \\
  %(package_upper)s_TYPE_%(object_upper)s))

#define %(package_upper)s_IS_%(object_upper)s_CLASS(klass) \\
  (G_TYPE_CHECK_CLASS_TYPE ((klass), \\
  %(package_upper)s_TYPE_%(object_upper)s))

#define %(package_upper)s_%(object_upper)s_GET_CLASS(obj) \\
  (G_TYPE_INSTANCE_GET_CLASS ((obj), \\
  %(package_upper)s_TYPE_%(object_upper)s, %(class_camel)sClass))

typedef struct _%(class_camel)s %(class_camel)s;
typedef struct _%(class_camel)sClass %(class_camel)sClass;
%(priv_typedef)s

struct _%(class_camel)s
{
  %(parent_camel)s parent;

%(priv_member)s
};

struct _%(class_camel)sClass
{
  %(parent_camel)sClass parent_class;
};

GType %(class_lower)s_get_type (void) G_GNUC_CONST;

%(class_camel)s *%(class_lower)s_new (void);

G_END_DECLS

#endif /* %(header_guard)s */
"""

c_template = """\
/* %(filename)s.c */

#include "%(filename)s.h"

%(define_type)s

%(private)s
%(interface_init)s
%(extra)s
%(class_init)s

static void
%(class_lower)s_init (%(class_camel)s *self)
{
%(priv_init)s
}

%(class_camel)s *
%(class_lower)s_new (void)
{
  return g_object_new (%(package_upper)s_TYPE_%(object_upper)s, NULL);
}
"""

private_template = """\
#define %(object_upper)s_PRIVATE(o) \\
  (G_TYPE_INSTANCE_GET_PRIVATE ((o), %(package_upper)s_TYPE_%(object_upper)s, %(class_camel)sPrivate))

struct _%(class_camel)sPrivate
{
};
"""

prop_template = """\
static void
%(class_lower)s_get_property (GObject *object, guint property_id, GValue *value, GParamSpec *pspec)
{
  switch (property_id)
    {
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
    }
}

static void
%(class_lower)s_set_property (GObject *object, guint property_id, const GValue *value, GParamSpec *pspec)
{
  switch (property_id)
    {
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
    }
}
"""

dispose_template = """\
static void
%(class_lower)s_dispose (GObject *object)
{
  G_OBJECT_CLASS (%(class_lower)s_parent_class)->dispose (object);
}
"""

finalize_template = """\
static void
%(class_lower)s_finalize (GObject *object)
{
  G_OBJECT_CLASS (%(class_lower)s_parent_class)->finalize (object);
}
"""
