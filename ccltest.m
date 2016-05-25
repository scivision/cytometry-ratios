% CCL test
function data = ccltest(dpath,flist,plotall)

if nargin<1; dpath = '../data/'; end
if nargin<2; flist = 'FRAME_1457.tif'; end
if nargin<3 
    if iscell(flist), plotall = false;
    else plotall = true;
    end
end
if ~iscell(flist), flist= {flist}; end
ifn = 0;
for cfn = flist
    ifn = ifn +1;
    cf = [dpath,cfn{1}];
    %% get image data 
    %here, the data is uint8
    data = imread(cf);
    [sy,sx] = size(data);

    datafloat = double(data);
    if plotall
        figure(100+ifn)
        %imagesc(data),
        imagesc(log10(datafloat)),
        title(['raw ',class(data),' data ',cf])
        hc = colorbar;
        ylabel(hc,'log_{10}(data)')
    end
    %% transparency mask
    mask = cat(3, ones(sy,sx), zeros(sy,sx), zeros(sy,sx) );  %all red image
    %% get vision toolbox handles
    h = gethandles;
    %% filter raw data
    filtered = wiener2(data,[5,5]);
    %% threshold (Otsu)
    [thres,thresval] = step(h.thres,filtered);
    display(['threshold value: ',num2str(thresval)])
    %if all(all(thres==false)) || all(all(thres==true)), error('bad thresholding'), end
    if plotall
        figure(2),imagesc(thres),colormap('gray'),title('thresholded')
    end
    %% morphological operations
    eroded = step(h.erosion,thres);

     if plotall
        figure(300+ifn),imagesc(eroded),colormap('gray'),title('morphological erosion')
        figure(1300+ifn),clf(1300+ifn)
        imagesc(data), hold('on'), colormap('gray')
        hm = imagesc(mask); %makes the image all red 
        set(hm,'AlphaData',0.5*eroded)
     end

    dilated = step(h.dilation,eroded);

    if plotall
        figure(4),imagesc(dilated),colormap('gray'),title('morphological dilation')
    end
        % plot result as overlay on original
        figure(1400+ifn),clf(1400+ifn)
        imagesc(datafloat), hold('on'), colormap('gray')
        hc = colorbar;
        ylabel(hc,'log_{10}(intensity)')
        hm = imagesc(mask); %makes the image all red 
        set(hm,'AlphaData',0.5*dilated)
        title(['raw ',class(data),' data, with cell detections in red',cf],'interpreter','none')
if ~nargout, clear('data'); end
end %for
end %function

function h = gethandles()

HugeStrel = strel('disk',9);
MidStrel = strel('disk',5);
SmallStrel = strel('disk',3);

h.erosion = vision.MorphologicalErode('NeighborhoodSource', 'Property', ...
                   'Neighborhood', SmallStrel);
h.dilation = vision.MorphologicalDilate('NeighborhoodSource', 'Property', ...
                   'Neighborhood', SmallStrel);           
h.thres = vision.Autothresholder('Operator', '>', ...
            'ThresholdScaleFactor', 0.75,...
            'ThresholdOutputPort',true);
end %function


