#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013-2014  Nick Hall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Location utility functions
"""
from ..lib.date import Today

#-------------------------------------------------------------------------
#
# get_location_list
#
#-------------------------------------------------------------------------
def get_location_list(db, place, date=None):
    """
    Return a list of place names for display.
    """
    if date is None:
        date = Today()
    visited = [place.handle]
    lines = [(place.name, place.get_type())]
    while True:
        handle = None
        for placeref in place.get_placeref_list():
            ref_date = placeref.get_date_object()
            if ref_date.is_empty() or date.match(ref_date):
                handle = placeref.ref
        if handle is None or handle in visited:
            break
        place = db.get_place_from_handle(handle)
        if place is None:
            break
        visited.append(handle)
        lines.append((place.name, place.get_type()))
    return lines

#-------------------------------------------------------------------------
#
# get_main_location
#
#-------------------------------------------------------------------------
def get_main_location(db, place, date=None):
    """
    Find all places in the hierarchy above the given place, and return the
    result as a dictionary of place types and names.
    """
    return dict([(int(place_type), name)
                    for name, place_type
                    in get_location_list(db, place, date)
                    if not place_type.is_custom()])

#-------------------------------------------------------------------------
#
# get_locations
#
#-------------------------------------------------------------------------
def get_locations(db, place):
    """
    Determine each possible route up the place hierarchy, and return a list
    containing dictionaries of place types and names.
    """
    locations = []
    todo = [(place, [(int(place.get_type()), place.get_all_names())],
            [place.handle])]
    while len(todo):
        place, tree, visited = todo.pop()
        for parent in place.get_placeref_list():
            if parent.ref not in visited:
                parent_place = db.get_place_from_handle(parent.ref)
                if parent_place is not None:
                    parent_tree = tree + [(int(parent_place.get_type()),
                                           parent_place.get_all_names())]
                    parent_visited = visited + [parent.ref]
                    todo.append((parent_place, parent_tree, parent_visited))
        if len(place.get_placeref_list()) == 0:
            locations.append(dict(tree))
    return locations

#-------------------------------------------------------------------------
#
# located_in
#
#-------------------------------------------------------------------------
def located_in(db, handle1, handle2):
    """
    Determine if the place identified by handle1 is located within the place
    identified by handle2.
    """
    place = db.get_place_from_handle(handle1)
    todo = [(place, [handle1])]
    while len(todo):
        place, visited = todo.pop()
        for parent in place.get_placeref_list():
            if parent.ref == handle2:
                return True
            if parent.ref not in visited:
                parent_place = db.get_place_from_handle(parent.ref)
                if parent_place is not None:
                    parent_visited = visited + [parent.ref]
                    todo.append((parent_place, parent_visited))
    return False
