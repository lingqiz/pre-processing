from flow.constants import ZABER_BASE, HS_BASE
from datetime import datetime
import os

'''
Generate a list of files to be processed for
p20 and p21 mice based on the start and end date

To use this script for other animals, change
`date_start` and `date_end` (line 26-27)
`animal = ` to the animal name folder (line 35)
and optionally change the skip condition between line 52-55
'''

# all mp4 files
files = [file for file in os.listdir(HS_BASE)
         if (os.path.isfile(os.path.join(HS_BASE, file)) and
             file.endswith('_hs.mp4'))]

# file time
file_time = []
for file in files:
    date_object = datetime.strptime(file[:15], '%Y%m%d_%H%M%S')
    file_time.append(date_object)

date_start = datetime.strptime('20240627', '%Y%m%d')
date_end = datetime.strptime('20241003', '%Y%m%d')

# filter files based on start and end date
files = [file for file, ft in zip(files, file_time)
         if (ft >= date_start and ft <= date_end)]
file_time = [ft for ft in file_time if (ft >= date_start and ft <= date_end)]

# all_params file
animal = 'p20p21'
csv_path = os.path.join(ZABER_BASE, animal)
csv_file = [file for file in os.listdir(csv_path)
            if (os.path.isfile(os.path.join(csv_path, file)) and
                file.endswith('.csv'))]

csv_time = []
for file in csv_file:
    date_object = datetime.strptime(file[:19], '%Y-%m-%dT%H_%M_%S')
    csv_time.append(date_object)

# write to file
file = open('file_names.txt', 'w')

for fl, ft in zip(files, file_time):
    # find the closest time in csv_time to ft
    time_diff = [abs(ft - ct) for ct in csv_time]
    min_index = time_diff.index(min(time_diff))

    # skip p19 and p22
    csv_str = csv_file[min_index]
    if (csv_str[20:23] == 'p19' or
        csv_str[20:23] == 'p22'):
        continue

    # skil large time difference (> 30 minute, likely mismatch)
    if time_diff[min_index].seconds > 1800:
        continue

    # file string for calibration
    file_str = '%s %s %s' % (animal, csv_str[:23], fl)

    # write to file
    file.write(file_str + '\n')
