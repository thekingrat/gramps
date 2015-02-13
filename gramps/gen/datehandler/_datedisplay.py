# -*- coding: utf-8 -*- 
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2013       Vassilii Khachaturov
# Copyright (C) 2014       Paul Franklin
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
U.S English date display class. Should serve as the base class for all
localized tasks.
"""
from __future__ import unicode_literals

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".DateDisplay")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from ..lib.date import Date
from . import _grampslocale
from ..utils.grampslocale import GrampsLocale
from ._datestrings import DateStrings

#-------------------------------------------------------------------------
#
# DateDisplay
#
#-------------------------------------------------------------------------
class DateDisplay(object):
    """
    Base date display class. 
    """
    _locale = GrampsLocale(lang='en_US', languages='en')

    _tformat = _grampslocale.tformat

    _ = _grampslocale.glocale.translation.sgettext
    formats = (
        # format 0 - must always be ISO
        _("YYYY-MM-DD (ISO)"), 

        # format # 1 - must always be locale-preferred numerical format
        # such as YY.MM.DD, MM-DD-YY, or whatever your locale prefers.
        # This should be the format that is used under the locale by 
        # strftime() for '%x'.
        # You may translate this as "Numerical", "System preferred", or similar.
        _("date format|Numerical"), 

        # Full month name, day, year
        _("Month Day, Year"), 

        # Abbreviated month name, day, year
        _("MON DAY, YEAR"), 

        # Day, full month name, year
        _("Day Month Year"), 

        # Day, abbreviated month name, year
        _("DAY MON YEAR")
        )
    """
    .. note:: Will be overridden if a locale-specific date displayer exists.

    If your localized :meth:`~_display_calendar`/:meth:`~_display_gregorian` 
    are overridden, you should override the whole formats list according
    to your own formats, and you need not localize the format names here.
    This ``formats`` must agree with
    :meth:`~_display_calendar`/:meth:`~_display_gregorian`.
    """
    del _

    newyear = ("", "Mar1", "Mar25", "Sep1")
    
    _bce_str = "%s B.C.E."
    # this will be overridden if a locale-specific date displayer exists

    def __init__(self, format=None):
        self._ds = DateStrings(self._locale)
        calendar = list(self._ds.calendar)
        calendar[Date.CAL_GREGORIAN] = "" # that string only used in parsing,
        # gregorian cal name shouldn't be output!
        self.calendar = tuple(calendar)
        self.short_months = self._ds.short_months
        self.swedish = self.long_months = self._ds.long_months
        self.hebrew = self._ds.hebrew
        self.french = self._ds.french
        self.persian = self._ds.persian
        self.islamic = self._ds.islamic
        self.display_cal = [
            self._display_gregorian, 
            self._display_julian, 
            self._display_hebrew, 
            self._display_french, 
            self._display_persian, 
            self._display_islamic, 
            self._display_swedish]
        self._mod_str = self._ds.modifiers
        self._qual_str = self._ds.qualifiers
        self.long_days = self._ds.long_days

        if format is None:
            self.format = 0
        else:
            self.format = format

        self._ = _ = self._locale.translation.sgettext
        self.FORMATS_long_month_year = {
# Inflection control due to modifier.
# Protocol: DateDisplayXX passes a key to the dictionary in the 
# parameter ``inflect`` to ``_display_calendar``.
# The modifier passed is not necessarily the one printed, it's just
# a representative that induces the same inflection control.
# For example, in Russian "before May", "after May", and "about May"
# all require genitive form for May, whereas no modifier (just "May 1234")
# require nominative, so DateDisplayRU.display will pass "before"
# in all 3 cases, collapsing the 3 modifiers into 1.
# 
# Another example in Russian is that "between April 1234 and June 1235"
# requires the same inflection for both April and June, so just "between"
# is used by DateDisplayRU.display, collapsing two more modifiers into 1.
#
# If inflect is not specified, then it means that the modifier doesn't have
# grammatical control over the format, and so the format can be
# localized in a context-free way.
# The translator is responsible for:
# 1) proper collapse of modifier classes
# 2) translating the formats that are selected in runtime
# 3) ignoring the other formats in .po (it does no harm to translate them,
# it's just a lot of extra work)
#
# To prevent POT pollution, not all possibilities are populated here yet.
# To be amended as the actual localized handlers use it.
#
# Not moving to DateStrings, as this is part of display code only,
# coupled tightly with the formats used in this file.
                ""
                : _("{long_month} {year}"),

                "from"
                # first date in a span
                # You only need to translate this string if you translate one of the
                # inflect=_("...") with "from"
                : _("from|{long_month} {year}"),

                "to"
                # second date in a span
                # You only need to translate this string if you translate one of the
                # inflect=_("...") with "to"
                : _("to|{long_month} {year}"),

                "between"
                # first date in a range
                # You only need to translate this string if you translate one of the
                # inflect=_("...") with "between"
                : _("between|{long_month} {year}"),

                "and"
                # second date in a range
                # You only need to translate this string if you translate one of the
                # inflect=_("...") with "and"
                : _("and|{long_month} {year}"),

                "before"
                # If "before <Month>" needs a special inflection in your
                # language, translate this to "{long_month.f[X]} {year}"
                # (where X is one of the month-name inflections you defined)
                : _("before|{long_month} {year}"),

                "after"
                # If "after <Month>" needs a special inflection in your
                # language, translate this to "{long_month.f[X]} {year}"
                # (where X is one of the month-name inflections you defined)
                : _("after|{long_month} {year}"),

                "about"
                # If "about <Month>" needs a special inflection in your
                # language, translate this to "{long_month.f[X]} {year}"
                # (where X is one of the month-name inflections you defined)
                : _("about|{long_month} {year}"),

            # TODO if no modifier, but with qual, might need to inflect in some lang.
        }

        self.FORMATS_short_month_year = {
                ""
                : _("{short_month} {year}"),

                "from" 
                # first date in a span
                : _("from|{short_month} {year}"),

                "to" 
                # second date in a span
                : _("to|{short_month} {year}"),

                "between" 
                # first date in a range
                : _("between|{short_month} {year}"),

                "and" 
                # second date in a range
                : _("and|{short_month} {year}"),

                "before" 
                # If "before <Month>" needs a special inflection in your
                # language, translate this to "{short_month.f[X]} {year}"
                # (where X is one of the month-name inflections you defined)
                : _("before|{short_month} {year}"),

                "after" 
                # If "after <Month>" needs a special inflection in your
                # language, translate this to "{short_month.f[X]} {year}"
                # (where X is one of the month-name inflections you defined)
                : _("after|{short_month} {year}"),

                "about" 
                # If "about <Month>" needs a special inflection in your
                # language, translate this to "{short_month.f[X]} {year}"
                # (where X is one of the month-name inflections you defined)
                : _("about|{short_month} {year}"),
        }

    def set_format(self, format):
        self.format = format

    def format_extras(self, cal, newyear):
        """
        Formats the extra items (calendar, newyear) for a date.
        """
        scal = self.calendar[cal]
        if isinstance(newyear, int) and newyear <= len(self.newyear):
            snewyear = self.newyear[newyear]
        elif isinstance(newyear, (list, tuple)):
            snewyear = "%s-%s" % (newyear[0], newyear[1])
        else:
            snewyear = "Err"
        retval = ""
        for item in [scal, snewyear]:
            if item:
                if retval:
                    retval += ", "
                retval += item
        if retval:
            return " (%s)" % retval
        return ""

    def display(self, date):
        """
        Return a text string representing the date.

        Disregard any format settings and use display_iso for each date.

        (Will be overridden if a locale-specific date displayer exists.)
        """
        mod = date.get_modifier()
        cal = date.get_calendar()
        qual = date.get_quality()
        start = date.get_start_date()
        newyear = date.get_new_year()

        qual_str = self._qual_str[qual]
        
        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN or mod == Date.MOD_RANGE:
            d1 = self.display_iso(start)
            d2 = self.display_iso(date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s %s - %s%s" % (qual_str, d1, d2, scal)
        else:
            text = self.display_iso(start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, scal)

    def _slash_year(self, val, slash):
        if val < 0:
            val = - val
            
        if slash:
            if (val-1) % 100 == 99:
                year = "%d/%d" % (val - 1, (val%1000))
            elif (val-1) % 10 == 9:
                year = "%d/%d" % (val - 1, (val%100))
            else:
                year = "%d/%d" % (val - 1, (val%10))
        else:
            year = "%d" % (val)
        
        return year
        
    def display_iso(self, date_val):
        # YYYY-MM-DD (ISO)
        year = self._slash_year(date_val[2], date_val[3])
        # This produces 1789, 1789-00-11 and 1789-11-00 for incomplete dates.
        if date_val[0] == date_val[1] == 0:
            # No month and no day -> year
            value = year
        else:
            value = "%s-%02d-%02d" % (year, date_val[1], date_val[0])
        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    def display_formatted(self, date):
        """
        Return a text string representing the date, according to the format.
        """
        mod = date.get_modifier()
        cal = date.get_calendar()
        qual = date.get_quality()
        start = date.get_start_date()
        newyear = date.get_new_year()

        qual_str = self._qual_str[qual]
        _ = self._
        
        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN:
            d1 = self.display_cal[cal](start, 
                    # If there is no special inflection for "from <Month>" in your
                    # language, don't translate this string.
                    # Otherwise, translate it to the ENGLISH!!! ENGLISH!!! 
                    # key appearing above in the FORMATS_... dict
                    # that maps to the special inflected format string that you need to localize.
                    inflect=_("from-date|"))
            d2 = self.display_cal[cal](date.get_stop_date(), 
                    # If there is no special inflection for "to <Month>" in your
                    # language, don't translate this string.
                    # Otherwise, translate it to the ENGLISH!!! ENGLISH!!! 
                    # key appearing above in the FORMATS_... dict
                    # that maps to the special inflected format string that you need to localize.
                    inflect=_("to-date|"))
            scal = self.format_extras(cal, newyear)
            return _("{date_quality}from {date_start} to {date_stop}"
                    "{nonstd_calendar_and_ny}").format(
                    date_quality=qual_str, 
                    date_start=d1, 
                    date_stop=d2, 
                    nonstd_calendar_and_ny=scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start,
                    # If there is no special inflection for "between <Month>" in your
                    # language, don't translate this string.
                    # Otherwise, translate it to the ENGLISH!!! ENGLISH!!! 
                    # key appearing above in the FORMATS_... dict
                    # that maps to the special inflected format string that you need to localize.
                    inflect=_("between-date|"))
            d2 = self.display_cal[cal](date.get_stop_date(),
                    # If there is no special inflection for "and <Month>" in your
                    # language, don't translate this string.
                    # Otherwise, translate it to the ENGLISH!!! ENGLISH!!! 
                    # key appearing above in the FORMATS_... dict
                    # that maps to the special inflected format string that you need to localize.
                    inflect=_("and-date|"))
            scal = self.format_extras(cal, newyear)
            return _("{date_quality}between {date_start} and {date_stop}"
                    "{nonstd_calendar_and_ny}").format(
                    date_quality=qual_str, 
                    date_start=d1, 
                    date_stop=d2, 
                    nonstd_calendar_and_ny=scal)
        else:
            if mod == Date.MOD_BEFORE:
                # If there is no special inflection for "before <Month>"
                # in your language, DON'T translate this string.  Otherwise,
                # "translate" this to "before" in ENGLISH!!! ENGLISH!!!
                date_type = _("before-date|")
            elif mod == Date.MOD_AFTER:
                # If there is no special inflection for "after <Month>"
                # in your language, DON'T translate this string.  Otherwise,
                # "translate" this to "after" in ENGLISH!!! ENGLISH!!!
                date_type = _("after-date|")
            elif mod == Date.MOD_ABOUT:
                # If there is no special inflection for "about <Month>"
                # in your language, DON'T translate this string.  Otherwise,
                # "translate" this to "about" in ENGLISH!!! ENGLISH!!!
                date_type = _("about-date|")
            else:
                date_type = ""
            text = self.display_cal[cal](start, inflect=date_type)
            scal = self.format_extras(cal, newyear)
            return _("{date_quality}{noncompound_modifier}{date}"
                    "{nonstd_calendar_and_ny}").format(
                    date_quality=qual_str, 
                    noncompound_modifier=self._mod_str[mod],
                    date=text, 
                    nonstd_calendar_and_ny=scal)

    def _display_gregorian(self, date_val, **kwargs):
        return self._display_calendar(date_val, self.long_months, 
                self.short_months, **kwargs)

    # Julian and Swedish date display is the same as Gregorian
    _display_julian = _display_swedish = _display_gregorian

    def format_long_month_year(self, month, year, inflect, long_months):
        if not hasattr(long_months[1], 'f'): # not a Lexeme: no inflection
            return "{long_month} {year}".format(
                     long_month = long_months[month], year = year)
        return self.FORMATS_long_month_year[inflect].format(
                     long_month = long_months[month], year = year)

    def format_short_month_year(self, month, year, inflect, short_months):
        if not hasattr(short_months[1], 'f'): # not a Lexeme: no inflection
            return "{short_month} {year}".format(
                     short_month = short_months[month], year = year)
        return self.FORMATS_short_month_year[inflect].format(
                     short_month = short_months[month], year = year)

    def format_long_month(self, month, inflect, long_months):
        if not hasattr(long_months[1], 'f'): # not a Lexeme: no inflection
            return "{long_month}".format(long_month = long_months[month])
        return self.FORMATS_long_month_year[inflect].format(
                     long_month = long_months[month], year = '').rstrip()

    def format_short_month(self, month, inflect, short_months):
        if not hasattr(short_months[1], 'f'): # not a Lexeme: no inflection
            return "{short_month}".format(short_month = short_months[month])
        return self.FORMATS_short_month_year[inflect].format(
                     short_month = short_months[month], year = '').rstrip()

    def dd_dformat01(self, date_val):
        """
        numerical

        this must agree with DateDisplayEn's "formats" definition
        (it may be overridden if a locale-specific date displayer exists)
        """
        if date_val[3]:
            return self.display_iso(date_val)
        else:
            if date_val[0] == date_val[1] == 0:
                return str(date_val[2])
            else:
                value = self._tformat.replace('%m', str(date_val[1]))
                if date_val[0] == 0: # ignore the zero day and its delimiter
                    i_day = value.find('%d')
                    value = value.replace(value[i_day:i_day+3], '')
                value = value.replace('%d', str(date_val[0]))
                value = value.replace('%Y', str(abs(date_val[2])))
                return value.replace('-', '/')

    def dd_dformat02(self, date_val, inflect, long_months):
        """
        month_name day, year

        this must agree with DateDisplayEn's "formats" definition
        (it may be overridden if a locale-specific date displayer exists)
        """
        _ = self._locale.translation.sgettext
        year = self._slash_year(date_val[2], date_val[3])
        if date_val[0] == 0:
            if date_val[1] == 0:
                return year
            else:
                return self.format_long_month_year(date_val[1], year,
                                                   inflect, long_months)
        else:
            # TRANSLATORS: this month is ALREADY inflected: ignore it
            return _("{long_month} {day:d}, {year}").format(
                       long_month = self.format_long_month(date_val[1],
                                                           inflect,
                                                           long_months),
                       day = date_val[0],
                       year = year)

    def dd_dformat03(self, date_val, inflect, short_months):
        """
        month_abbreviation day, year

        this must agree with DateDisplayEn's "formats" definition
        (it may be overridden if a locale-specific date displayer exists)
        """
        _ = self._locale.translation.sgettext
        year = self._slash_year(date_val[2], date_val[3])
        if date_val[0] == 0:
            if date_val[1] == 0:
                return year
            else:
                return self.format_short_month_year(date_val[1], year,
                                                    inflect, short_months)
        else:
            # TRANSLATORS: this month is ALREADY inflected: ignore it
            return _("{short_month} {day:d}, {year}").format(
                       short_month = self.format_short_month(date_val[1],
                                                             inflect,
                                                             short_months),
                       day = date_val[0],
                       year = year)

    def dd_dformat04(self, date_val, inflect, long_months):
        """
        day month_name year

        this must agree with DateDisplayEn's "formats" definition
        (it may be overridden if a locale-specific date displayer exists)
        """
        _ = self._locale.translation.sgettext
        year = self._slash_year(date_val[2], date_val[3])
        if date_val[0] == 0:
            if date_val[1] == 0:
                return year
            else:
                return self.format_long_month_year(date_val[1], year,
                                                   inflect, long_months)
        else:
            # TRANSLATORS: this month is ALREADY inflected: ignore it
            return _("{day:d} {long_month} {year}").format(
                       day = date_val[0],
                       long_month = self.format_long_month(date_val[1],
                                                           inflect,
                                                           long_months),
                       year = year)

    def dd_dformat05(self, date_val, inflect, short_months):
        """
        day month_abbreviation year

        this must agree with DateDisplayEn's "formats" definition
        (it may be overridden if a locale-specific date displayer exists)
        """
        _ = self._locale.translation.sgettext
        year = self._slash_year(date_val[2], date_val[3])
        if date_val[0] == 0:
            if date_val[1] == 0:
                return year
            else:
                return self.format_short_month_year(date_val[1], year,
                                                    inflect, short_months)
        else:
            # TRANSLATORS: this month is ALREADY inflected: ignore it
            return _("{day:d} {short_month} {year}").format(
                       day = date_val[0],
                       short_month = self.format_short_month(date_val[1],
                                                             inflect,
                                                             short_months),
                       year = year)

    def _display_calendar(self, date_val, long_months, short_months = None,
                          inflect=""):
        """
        this must agree with DateDisplayEn's "formats" definition
        (it may be overridden if a locale-specific date displayer exists)
        """

        if short_months is None:
            # Let the short formats work the same as long formats
            short_months = long_months

        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:
            # numerical
            value = self.dd_dformat01(date_val)
        elif self.format == 2:
            # month_name day, year
            value = self.dd_dformat02(date_val, inflect, long_months)
        elif self.format == 3:
            # month_abbreviation day, year
            value = self.dd_dformat03(date_val, inflect, short_months)
        elif self.format == 4:
            # day month_name year
            value = self.dd_dformat04(date_val, inflect, long_months)
        # elif self.format == 5:
        else:
            # day month_abbreviation year
            value = self.dd_dformat05(date_val, inflect, short_months)
        if date_val[2] < 0:
            # TODO fix BUG 7064: non-Gregorian calendars wrongly use BCE notation for negative dates
            return self._bce_str % value
        else:
            return value


    def _display_french(self, date_val, **kwargs):
        return self._display_calendar(date_val, self.french, **kwargs)

    def _display_hebrew(self, date_val, **kwargs):
        return self._display_calendar(date_val, self.hebrew, **kwargs)

    def _display_persian(self, date_val, **kwargs):
        return self._display_calendar(date_val, self.persian, **kwargs)

    def _display_islamic(self, date_val, **kwargs):
        return self._display_calendar(date_val, self.islamic, **kwargs)

class DateDisplayEn(DateDisplay):
    """
    English language date display class. 
    """


    def __init__(self, format=None):
        """
        Create a DateDisplay class that converts a Date object to a string
        of the desired format. The format value must correspond to the format
        list value (DateDisplay.format[]).
        """

        DateDisplay.__init__(self, format)

    display = DateDisplay.display_formatted

    _locale = _grampslocale.glocale # normally set in register_datehandler
