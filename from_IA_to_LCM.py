import sys
import os
import pandas as pd
import numpy as np
import numpy.linalg
import re

# amount of rotation to add in degrees
add_rotation = 0


def do_transformation(list_of_tuples, A):

    for i, point in enumerate(list_of_tuples):
        list_of_tuples[i] = A.dot(point+(1.0,))


def write_header(fid, version, date, time, delimiter):
    fid.write('PALMRobo Elements\n')
    fid.write(delimiter.join(('Version:', '"{}"'.format(version))) + '\n')
    fid.write(delimiter.join(('Date, Time:', date, time)) + '\n')
    fid.write('\n')
    fid.write('MICROMETER\n')
    fid.write('Elements :\n')
    fid.write('\n')


def calculate_transform_matrix(x, xp):
    X = np.kron(np.eye(2), np.concatenate((x, np.ones((x.shape[0], 1))), axis=1))
    b = np.concatenate((xp[:, 0], xp[:, 1])).reshape((2*x.shape[0], 1))

    a, residuals, rank, s = np.linalg.lstsq(X, b, rcond=None)

    print('residuals = \n{}'.format(residuals))

    A = np.array([
        [a[0, 0], a[1, 0], a[2, 0]],
        [a[3, 0], a[4, 0], a[5, 0]],
        [0, 0, 1],
    ])

    r = np.radians(add_rotation)
    rot = np.array([
        [np.cos(r), -np.sin(r), 0],
        [np.sin(r), np.cos(r), 0],
        [0, 0, 1],
    ])

    A = A.dot(rot)

    print('A = \n{}'.format(A))

    return A


def calculate_transform():
    filename = 'reference_points.dat'
    ref_pt_file = open(filename, 'r')
    line = ref_pt_file.readline()
    if line[:3] != '#ia':
        raise RuntimeError('Expecting 1st line of {} to be "#ia"')

    point_regex = re.compile(r'\(\s*([0-9\.]+)\s*\,\s*([0-9\.]+\s*)\)')
    lcm_regex = re.compile(r'\(\s*([0-9\.]+)\s*\,\s*([0-9\.]+\s*)\)')
    line = ref_pt_file.readline()

    ia_points = []
    while '#lcm' not in line:
        m = point_regex.match(line)
        if m is None:
            print(
                'Warning: line "{}" did not match point format "(x,y)", ignoring...'.format(line[:-1]))
        else:
            x = m.group(1)
            y = m.group(2)
            ia_points.append([x, y])

        line = ref_pt_file.readline()
    n_points = len(ia_points)
    ia_points = np.array(ia_points, dtype=float)

    print('IA points = \n{}'.format(ia_points))

    line = ref_pt_file.readline()
    lcm_points = []
    while line:
        m = point_regex.match(line)
        if m is None:
            print(
                'Warning: line "{}" did not match point format "(x,y)", ignoring...'.format(line[:-1]))
        else:
            x = m.group(1)
            y = m.group(2)
            lcm_points.append([x, y])

        line = ref_pt_file.readline()
    if len(lcm_points) != n_points:
        raise RuntimeError('Number of ia points({}), is not equal to the number of \
                            lcm points ({})'.format(n_points, len(lcm_points)))
    lcm_points = np.array(lcm_points, dtype=float)
    print('LCM points = \n{}'.format(lcm_points))

    return calculate_transform_matrix(ia_points, lcm_points)


version = 'V 4.8.0.1'
date = '26/11/18'
time = '17:20:54'
column_names = ["Type", "Color", "Thickness", "No",
                "CutShot", "Area", "Z", "Comment", "Coordinates"]
delimiter = '\t'


try:
    file_to_convert = sys.argv[1]
except IndexError:
    sys.exit('Error: No input file\nUsage: python {} input_file'.format(sys.argv[0]))

# Open input IA file and output csv file
try:
    IA_file = open(file_to_convert, 'r')
except:
    sys.exit('Error: File {} not found'.format(file_to_convert))

# Open output CSV file
rootname, ext = os.path.splitext(file_to_convert)
converted_file = '{}_converted_to_LCM.csv'.format(rootname)
if os.path.isfile(converted_file):
    os.remove(converted_file)
csv_file = open(converted_file, 'a', newline='\r\n')

write_header(csv_file, version, date, time, delimiter)

csv_file.write(delimiter.join(column_names))
csv_file.write('\n\n')

df_head = pd.read_csv('values.csv', sep='\t', names=column_names)

A = calculate_transform()

for i, line in enumerate(IA_file):
    # Write first two rows
    df_head[i:i+1].to_csv(csv_file, sep=delimiter, index=False, header=False)

    # Parse IA file and build list of tuples (x,y)
    line = line.split(":")

    filter_start = [s.startswith(' ') for s in line]
    filtered_list = [i.replace(', Point', '').strip()
                     for (i, v) in zip(line, filter_start) if v]
    filtered_list[-1] = filtered_list[-1].replace(']', '')

    list_of_tuples = [(float(s.split(', ')[0]), float(s.split(', ')[1]))
                      for s in filtered_list]

    do_transformation(list_of_tuples, A)

    # Convert list of tuples to list of string
    # ["x1,y1", "x2,y2"...]
    list_of_strings = ['{:.1f},{:.1f}'.format(t[0], t[1]) for t in list_of_tuples]

    # Reshape list of strings into a list of lists.
    # Each sublist has 5 elements
    # If the length of the original list_of_strings is not a multiple
    # of 5, then the remaining elements are gathered into rest_list
    # This list is padded with empty characters and added to the full list.
    nb_sublists = len(list_of_strings)//5
    N = len(list_of_strings)

    iterator = iter(list_of_strings)
    alist = [[next(iterator) for _ in range(5)] for sublist in range(nb_sublists)]

    if N % 5:
        rest_list = list_of_strings[-(N % 5):]
        rest_list = rest_list + ['']*(5-len(rest_list))
        alist.append(rest_list)

    # Add dot in position 0 for each sublist
    for sublist in alist:
        sublist.insert(0, ".")

    # Build pandas DataFrame from list of lists
    # and update output csv file
    df = pd.DataFrame(alist)
    df.to_csv(csv_file, sep=delimiter, index=False, header=False)

    # Jump to lines and loop back to next line in IA input file
    csv_file.write('\n\n')
