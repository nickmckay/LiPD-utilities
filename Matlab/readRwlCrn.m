
function T = readRwlCrn(pathToFiles,varargin)


if nargin <1
    [pathToFiles] = uigetdir('.','Select the folder with the .rwl and/or .crn files you want to load in');
end
    

%find the files in the folder
curdir = cd;
cd(pathToFiles);
rwld = dir('*.rwl');
crnd =  dir('*.crn');


if nargin>1
opt = varargin2struct(varargin{:});
else
    opt = struct;
end



% At a minimum, we need: 
% Dataset name
if ~isfield(opt,'datasetname')
    opt.datasetname = input('Input your dataset name as a string: ');
end
    siteID = makeValidName(opt.datasetname);
T.(siteID).Name = siteID;
    
    
% Lat (under Spatial_coverage)
if ~isfield(opt,'latitude')
    opt.latitude = input('Input the site latitude in decimal degrees: ');
end
T.(siteID).lat=opt.latitude;

% Lon
if ~isfield(opt,'longitude')
    opt.longitude = input('Input the site longitude in decimal degrees: ');
end
T.(siteID).lon=opt.longitude;

% Elevation
if isfield(opt,'elevation')
T.(siteID).elev=opt.elevation;
end


if length(rwld) >0
    % loop through all the rwl files
    count=1;
    for i =1:length(rwld);
        
        fileName=rwld(i).name;
        recName=fileName(1:end-4);
        fileType= fileName(end-2:end);
        
        % If no local copy exists, go get it:
        %clear to make sure no leftovers from last loop
        clear x yr s X yrX nms Tvalid
        switch fileType
            case 'crn'
                [x,s,yr]=crn2vec2(fileName);
                T.(siteID).(recName).chronology.filename=fileName;
                %T.(siteID).(recName).chronology.url=url;
                T.(siteID).(recName).chronology.ID=recName;
                T.(siteID).(recName).chronology.Data=x;
                T.(siteID).(recName).chronology.Time=yr;
                T.(siteID).(recName).chronology.nSamp=s;
                
            case 'rwl'
                [X,yrX,nms,Tvalid]=rwl2tsm(fileName);
                T.(siteID).(recName).measurements.filename=fileName;
                %T.(siteID).(recName).measurements.url=url;
                T.(siteID).(recName).measurements.ID=nms;
                T.(siteID).(recName).measurements.Data=X;
                T.(siteID).(recName).measurements.Time=yrX;
                T.(siteID).(recName).measurements.Tvalid=Tvalid;
                
                
        end
        count=count+1;
    end
    
end

if length(crnd) >0
    % loop through all the rwl files
    count=1;
    for i =1:length(crnd);
        
        fileName=crnd(i).name;
        recName=fileName(1:end-4);
        fileType= fileName(end-2:end);
        
        % If no local copy exists, go get it:
        %clear to make sure no leftovers from last loop
        clear x yr s X yrX nms Tvalid
        switch fileType
            case 'crn'
                crnCell=getCrns(fileName);
                T.(siteID).(recName).chronology.filename=fileName;
                T.(siteID).(recName).chronology.crnCell=getCrns(fileName);
% 
%                 %T.(siteID).(recName).chronology.url=url;
%                 T.(siteID).(recName).chronology.ID=recName;
%                 T.(siteID).(recName).chronology.Data=x;
%                 T.(siteID).(recName).chronology.Time=yr;
%                 T.(siteID).(recName).chronology.nSamp=s;
                
            case 'rwl'
                [X,yrX,nms,Tvalid]=rwl2tsm(fileName);
                T.(siteID).(recName).measurements.filename=fileName;
                %T.(siteID).(recName).measurements.url=url;
                T.(siteID).(recName).measurements.ID=nms;
                T.(siteID).(recName).measurements.Data=X;
                T.(siteID).(recName).measurements.Time=yrX;
                T.(siteID).(recName).measurements.Tvalid=Tvalid;
                
                
        end
        count=count+1;
    end
    
end

cd(curdir)







end
