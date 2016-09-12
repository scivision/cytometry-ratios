clear, clc, close('all')

dpath = '../data/';

flist = {'FRAME_1457.tif','FRAME_1458.tif','FRAME_1459.tif',...
    'FRAME_1460.tif','FRAME_1461.tif','FRAME_1462.tif'};
data = ccltest(dpath,flist);