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

#ifndef %(header-guard)s
#define %(header-guard)s

#include <glib-object.h>

G_BEGIN_DECLS

#define %(package-upper)s_TYPE_%(object-upper)s %(class-lower)s_get_type()

#define %(package-upper)s_%(object-upper)s(obj) \\
  (G_TYPE_CHECK_INSTANCE_CAST ((obj), \\
  %(package-upper)s_TYPE_%(object-upper)s, %(class-camel)s))

#define %(package-upper)s_%(object-upper)s_CLASS(klass) \\
  (G_TYPE_CHECK_CLASS_CAST ((klass), \\
  %(package-upper)s_TYPE_%(object-upper)s, %(class-camel)sClass))

#define %(package-upper)s_IS_%(object-upper)s(obj) \\
  (G_TYPE_CHECK_INSTANCE_TYPE ((obj), \\
  %(package-upper)s_TYPE_%(object-upper)s))

#define %(package-upper)s_IS_%(object-upper)s_CLASS(klass) \\
  (G_TYPE_CHECK_CLASS_TYPE ((klass), \\
  %(package-upper)s_TYPE_%(object-upper)s))

#define %(package-upper)s_%(object-upper)s_GET_CLASS(obj) \\
  (G_TYPE_INSTANCE_GET_CLASS ((obj), \\
  %(package-upper)s_TYPE_%(object-upper)s, %(class-camel)sClass))

typedef struct _%(class-camel)s %(class-camel)s;
typedef struct _%(class-camel)sClass %(class-camel)sClass;
%(priv-typedef)s

struct _%(class-camel)s
{
  %(parent-camel)s parent;

%(priv-member)s
};

struct _%(class-camel)sClass
{
  %(parent-camel)sClass parent_class;
};

GType %(class-lower)s_get_type (void) G_GNUC_CONST;

%(class-camel)s *%(class-lower)s_new (void);

G_END_DECLS

#endif /* %(header-guard)s */
"""

c_template = """\
/* %(filename)s.c */

#include "%(filename)s.h"

%(define-type)s

%(private)s
%(interface-init)s
%(extra)s
%(class-init)s

static void
%(class-lower)s_init (%(class-camel)s *self)
{
%(priv-init)s
}

%(class-camel)s *
%(class-lower)s_new (void)
{
  return g_object_new (%(package-upper)s_TYPE_%(object-upper)s, NULL);
}
"""

private_template = """\
#define %(object-upper)s_PRIVATE(o) \\
  (G_TYPE_INSTANCE_GET_PRIVATE ((o), %(package-upper)s_TYPE_%(object-upper)s, %(class-camel)sPrivate))

struct _%(class-camel)sPrivate
{
};
"""

prop_template = """\
static void
%(class-lower)s_get_property (GObject    *object,
%(function-len)s  guint       property_id,
%(function-len)s  GValue     *value,
%(function-len)s  GParamSpec *pspec)
{
  switch (property_id)
    {
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
    }
}

static void
%(class-lower)s_set_property (GObject      *object,
%(function-len)s  guint         property_id,
%(function-len)s  const GValue *value,
%(function-len)s  GParamSpec   *pspec)
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
%(class-lower)s_dispose (GObject *object)
{
  G_OBJECT_CLASS (%(class-lower)s_parent_class)->dispose (object);
}
"""

finalize_template = """\
static void
%(class-lower)s_finalize (GObject *object)
{
  G_OBJECT_CLASS (%(class-lower)s_parent_class)->finalize (object);
}
"""
