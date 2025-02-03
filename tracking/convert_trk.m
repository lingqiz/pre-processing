file_base = '/groups/dennis/dennislab/data/hs_cam';
fid = fopen('./track_names.txt', 'r');

while ~feof(fid) % Loop until end of file
    % read in file names
    line = fgetl(fid);
    file_name = strcat(line, '.trk');
    disp(file_name);

    % read tracking result
    file_path = fullfile(file_base, file_name);
    trk_data = load(file_path, '-mat');

    points = trk_data.pTrk{:};
    conf = trk_data.pTrkConf{:};
    start_frame = trk_data.startframes;
    end_frame = trk_data.endframes;

    % save file
    str_len = length(file_path);
    file_path(str_len - 2:end) = 'mat';
    save(file_path, 'points', 'conf', ...
        'start_frame', 'end_frame');
end