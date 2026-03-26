% Setup path 
run('/groups/zhang/home/zhangl5/JAABA/perframe/SetUpJAABAPath.m');

expdir = '/groups/dennis/dennislab/data/new_format/p16/p16_2024-02-22-09-46-32';
jabfiles = {'/groups/dennis/dennislab/lingqi/03202026_Rearing.jab',
    '/groups/dennis/dennislab/lingqi/03202026_Grooming.jab'};

JAABADetect(expdir, 'jabfiles', jabfiles, 'forcecompute', true);
