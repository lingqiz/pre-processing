from flow.constants import ZABER_BASE, HS_BASE
from datetime import datetime
import os 

# all mp4 files
files = [file for file in os.listdir(HS_BASE) 
         if (os.path.isfile(os.path.join(HS_BASE, file)) and 
             file.endswith('_hs.mp4'))]

# file time
file_time = []
for file in files:
    date_object = datetime.strptime(file[:15], '%Y%m%d_%H%M%S')
    file_time.append(date_object)

date_start = datetime.strptime('20240304', '%Y%m%d')
date_end = datetime.strptime('20240528', '%Y%m%d')

# filter files based on start and end date
files = [file for file, ft in zip(files, file_time) 
         if (ft >= date_start and ft <= date_end)]
file_time = [ft for ft in file_time if (ft >= date_start and ft <= date_end)]

# all_params file
animal = 'p16p17p18'
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
    
    # file string
    file_str = '%s %s %s' % (animal, csv_file[min_index][:23], fl)
    
    # write to file
    file.write(file_str + '\n')
    