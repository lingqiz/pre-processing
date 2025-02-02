import os

input_file = "track_names.txt"
bash_script = "./run_track.sh"

with open(input_file, "r") as file:
    file_names = [line.strip() for line in file if line.strip()] 
    
for fl in file_names:
    os.system(f"bash {bash_script} {fl}")