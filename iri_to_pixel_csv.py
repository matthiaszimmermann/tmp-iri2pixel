import datetime
import os
import sys

# add relative path to pythonpath so this works when calling from the project root folder
# sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from util.geo import latitude_longitude_to_pixel, pixel_to_latitude_longitude
from util.timestamp import LocalDate

NO_DATA = '999.0'

DAYS = 366

MONTH = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec'
}

DAY = {
    1: 31,
    2: 29,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}

def header(year_from):
    header = ['""']

    for year in range(year_from, current_year() + 1):
        header.append('"{}"'.format(year))
    
    return header

def current_year():
    return date_to_year(datetime.datetime.now())

def date_to_year(date):
    return int(date.strftime("%Y"))

def to_date_string(month, day):
    return '"{}-{}"'.format(day, MONTH[month])

def get_args():    
    if len(sys.argv) != 6:
        print('usage: {} file x y year-from dir-out'.format(sys.argv[0]))
        sys.exit(1)
    
    (file_name_in, latitude, longitude, year_from, out_dir) = sys.argv[1:]
    pixel = latitude_longitude_to_pixel(float(latitude), float(longitude))
    file_name_out = '{}/{}.csv'.format(out_dir, pixel)

    return (file_name_in, file_name_out, pixel, out_dir, int(year_from))

def get_iri_dict(filename):
    rainfall_dict = {}

    header = True
    with open(filename) as file:
        while (line := file.readline().strip()):
            if not header:
                tok = line.split(',')
                date = LocalDate.from_custom(tok[0], '%d %b %Y')
                date_key = LocalDate.to_compact(date)
                rainfall_dict[date_key] = tok[1]
            else:
                header = False
    
    return rainfall_dict

def get_data(file_name_in, year_from):
    rows = DAYS
    cols = current_year() - year_from + 1
    data = create_array(rows, cols)

    iri_dict = get_iri_dict(file_name_in)

    for year in range(year_from, current_year() + 1):
        date = datetime.date(year=year,day=1,month=1)
        #rainfall = get_arc2_data(pixel, date)
        rainfall = get_iri_data(iri_dict, date)

        if rainfall.startswith('error'):
            print('problem during rainfall request: {}. exiting ...'.format(rainfall))
            sys.exit(1)
    
        for line in rainfall.split('\n'):
            if len(line) == 0:
                continue

            tok = line.split(' ')

            if len(tok) != 2:
                print('problem during rainfall data parsing, line content "{}", exiting ...'.format(line))
                sys.exit(2)

            if not tok[0].startswith(str(year)):
                continue

            rain_date = LocalDate.from_compact(tok[0])
            rain_amount = tok[1]

            if rain_amount == '999.0':
                continue

            row = to_row_index(rain_date, year_from)
            col = to_column_index(rain_date, year_from)
            data[row][col] = rain_amount

    return data

def create_array(rows, cols, element=''):
    array = []

    for i in range(rows):
        array.append(create_list(cols, element))

    return array

def create_list(cols, element):
    col = []

    for j in range(cols):
        col.append(element)

    return col

def to_column_index(date, year_from):
    year = date_to_year(date)
    return year - year_from

def to_row_index(date, year_from):
    tt = date.timetuple()
    day_of_year = tt.tm_yday
    year = tt.tm_year

    if day_of_year <= 59:
        return day_of_year - 1
    elif is_leap_year(year):
        return day_of_year - 1

    return day_of_year

def is_leap_year(year):
    if year % 400 == 0:
        return True
    elif year % 100 == 0:
        return False
    elif year % 4 == 0:
        return True

    return False

def get_iri_data(iri_dict, date):
    day_from = date.toordinal()
    day_to = day_from + DAYS

    rainfall = []

    for day in range(day_from, day_to):
        date_rainfall = LocalDate.from_ordinal(day)
        date_key = LocalDate.to_compact(date_rainfall)

        if date_key in iri_dict:
            rainfall.append('{} {}'.format(date_key, iri_dict[date_key]))
        else:
            rainfall.append('{} {}'.format(date_key, NO_DATA))

    return '\n'.join(rainfall)

def get_arc2_data(pixel, date):
    request_params = {}
    (request_params[ARC2_LATITUDE], request_params[ARC2_LONGITUDE]) = pixel_to_latitude_longitude(pixel)
    request_params[ARC2_DATE] = LocalDate.to_compact(date)
    request_params[ARC2_DAYS] = DAYS

    try:
        response = requests.get(ARC2_URL, params=request_params, timeout=ARC2_TIMEOUT)
        return response.text
        
    except Exception as e:
        return "error calling arc2 server {}".format(e)

# https://www.h2kinfosys.com/blog/reading-and-writing-csv-files-in-python-using-csv-module-pandas/
def main():
    (file_name_in, file_name_out, pixel, out_dir, year_from) = get_args()
    data = get_data(file_name_in, year_from)

    with open(file_name_out, 'w') as csvfile:
        csvfile.write('{}\n'.format(','.join(header(year_from))))

        row = 0
        for month, name in MONTH.items():
            for day in range(1, DAY[month] + 1):
                csvfile.write('{},{}\n'.format(to_date_string(month, day), ','.join(data[row])))
                row += 1

if __name__ == "__main__":
    main()
