import sys
import os
import pandas as pd

def do_transformation(list_of_tuples):
    pass

def write_header(fid, version, date, time):
    fid.write('PALMRobo Elements\n')
    fid.write('Version:,{}\n'.format(version))
    fid.write('Date, Time:,{},{}\n'.format(date,time))
    fid.write('\n')
    fid.write('MICROMETER\n')
    fid.write('Elements :\n')
    fid.write('\n')
    
version='V 4.8.0.1'
date='26/11/18'
time='17:20:54'
column_names = ["Type", "Color", "Thickness", "No", "CutShot", "Area", "Z", "Comment", "Coordinates"]

try:
    file_to_convert = sys.argv[1]
except IndexError:
    sys.exit('Error: No input file\nUsage: python {} input_file'.format(sys.argv[0]))

# Open input IA file and output csv file
try:
    IA_file = open(file_to_convert, 'r');
except:
    sys.exit('Error: File {} not found'.format(file_to_convert))
    
# Open output CSV file
rootname, ext = os.path.splitext(file_to_convert)
converted_file = '{}_converted_to_LCM.csv'.format(rootname)
if os.path.isfile(converted_file):
    os.remove(converted_file)
csv_file = open(converted_file, 'a')
    
write_header(csv_file, version, date, time)

for s in column_names[:-1]:
    csv_file.write('{},'.format(s))
csv_file.write('{}'.format(column_names[-1]))
csv_file.write('\n\n')

df_head = pd.read_csv('values.csv', sep='\t', names=column_names)



for i, line in enumerate(IA_file):
    # Write first two rows
    df_head[i:i+1].to_csv(csv_file, sep=',',index=False, header=False)

    #Parse IA file and build list of tuples (x,y)
    line = line.split(":")

    filter_start = [s.startswith(' ') for s in line]
    filtered_list = [i.replace(', Point','').strip() for (i, v) in zip(line, filter_start) if v]
    filtered_list[-1] = filtered_list[-1].replace(']','')

    list_of_tuples = [(float(s.split(', ')[0]),float(s.split(', ')[1])) for s in filtered_list]

    do_transformation(list_of_tuples)

    # Convert list of tuples to list of string
    # ["x1,y1", "x2,y2"...]
    list_of_strings = ['{},{}'.format(t[0],t[1]) for t in list_of_tuples]

    # Reshape list of strings into a list of lists.
    # Each sublist has 5 elements
    # If the length of the original list_of_strings is not a multiple
    # of 5, then the remaining elements are gathered into rest_list
    # This list is padded with empty characters and added to the full list.
    nb_sublists = len(list_of_strings)//5
    N = len(list_of_strings)

    iterator = iter(list_of_strings)
    alist = [[next(iterator) for _ in range(5)] for sublist in range(nb_sublists)]

    if N%5:
        rest_list = list_of_strings[-(N%5):]
        rest_list = rest_list + ['']*(5-len(rest_list))
        alist.append(rest_list)
        
    # Add dot in position 0 for each sublist
    for sublist in alist:
        sublist.insert(0,".")
        
    # Build pandas DataFrame from list of lists
    # and update output csv file
    df = pd.DataFrame(alist)
    df.to_csv(csv_file, sep=',',index=False, header=False)

    # Jump to lines and loop back to next line in IA input file
    csv_file.write('\n\n')

