# https://stackoverflow.com/questions/4563272/how-to-convert-a-utc-datetime-to-a-local-datetime-using-only-standard-library/13287083#13287083
# https://pythonhosted.org/pytz/

import logging
import re

from datetime import tzinfo, timedelta, datetime
from pprint import pprint


class TimeZoneInfoUtc(tzinfo):

    def __init__(self, offset=0, name=None):
        self.offset = timedelta(seconds=offset)
        self.name = name or self.__class__.__name__

    def utcoffset(self, dt):
        return self.offset

    def tzname(self, dt):
        return self.name

    def dst(self, dt):
        return timedelta(0)


class LocalDate(object):

    # https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
    # YYYY-MM-DD
    ISO_DATE_FORMAT = '%Y-%m-%d'
    COMPACT_FORMAT = '%Y%m%d'

    @staticmethod
    def from_timestamp(ts):
        d_unaware = datetime(ts.year, ts.month, ts.day)
        return d_unaware

    @staticmethod
    def from_ordinal(date):
        d_unaware = datetime.fromordinal(date)
        return d_unaware

    @staticmethod
    def from_isoformat(date_str):
        if not date_str:
            logging.debug("provided date string is None, returning None instead of date")
            return None
        
        return datetime.strptime(date_str, LocalDate.ISO_DATE_FORMAT)

    @staticmethod
    def to_isoformat(dt):
        if not dt:
            logging.debug("provided string is None, returning None instead of iso date string")
            return None
        
        if isinstance(dt, str):
            if re.match(r"20[1-5][0-9]-[0-1][0-9]-[0-3][0-9]", dt):
                return dt
            else:
                logging.warning("provided string is no iso date (YYYY-MM-DD) {}".format(dt))
                return None
        
        return dt.strftime(LocalDate.ISO_DATE_FORMAT)

    @staticmethod
    def from_compact(date_str):
        return datetime.strptime(date_str, LocalDate.COMPACT_FORMAT)

    @staticmethod
    def to_compact(dt):
        return dt.strftime(LocalDate.COMPACT_FORMAT)

    @staticmethod
    def from_custom(date_str, format):
        return datetime.strptime(date_str, format)

    @staticmethod
    def to_custom(dt, format):
        return dt.strftime(format)

    @staticmethod
    def isoformat_to_ordinal(date_isoformat):
        date = LocalDate.from_isoformat(date_isoformat)
        return date.toordinal()

    @staticmethod
    def ordinal_to_isoformat(date_ordinal):
        date = LocalDate.from_ordinal(date_ordinal)
        return LocalDate.to_isoformat(date)

def main():

    ts = LocalizedTimeStamp.now_utc()
    print("LocalizedTimeStamp.now_utc() {}".format(ts))

    for tz in LocalizedTimeStamp.TIMEZONES:
        print("{} ({})".format(LocalizedTimeStamp.utc_to_local(ts, tz), tz))

    ts_nairobi = LocalizedTimeStamp.utc_to_local(ts, LocalizedTimeStamp.NAIROBI)
    print("ts_nairobi.to_isoformat() {}".format(LocalizedTimeStamp.to_isoformat(ts_nairobi)))

    print("---")

    ts_from_string = LocalizedTimeStamp.from_isoformat('2011-11-04T00:05:23+04:00')
    ts_to_utc = LocalizedTimeStamp.local_to_utc(ts_from_string)

    print("fromisoformat('2011-11-04T00:05:23+04:00') {}".format(ts_from_string))
    print("LocalizedTimeStamp.local_to_utc(ts_from_string) {}".format(ts_to_utc))

    ts_string_minus = '2011-11-04T00:05:23-02:00'
    ts_from_string_minus = LocalizedTimeStamp.from_isoformat(ts_string_minus)
    ts_to_utc_minus = LocalizedTimeStamp.local_to_utc(ts_from_string_minus)

    print("fromisoformat('{}') {}".format(ts_string_minus, ts_from_string_minus))
    print("LocalizedTimeStamp.local_to_utc(ts_from_string) {}".format(ts_to_utc_minus))

    ts_unaware = datetime.now()
    ts_now_utc = LocalizedTimeStamp.local_to_utc(ts_unaware, LocalizedTimeStamp.CET)
    ts_now_nairobi = LocalizedTimeStamp.utc_to_local(ts_now_utc, LocalizedTimeStamp.NAIROBI)

    print("ts {}\n-> utc {}\n-> nairobi {}".format(ts_unaware, ts_now_utc, ts_now_nairobi))
    print("--------")

    d_210615 = LocalDate.from_isoformat('2021-06-15')
    print("LocalDate.from_isoformat('2021-06-21-15') {}".format(d_210615))

    ts_now = datetime.now()
    d_now = LocalDate.from_timestamp(ts_now)

    print("now {} LocalDate.from_datetime() {}".format(ts_now, d_now))

if __name__ == "__main__":
    main()