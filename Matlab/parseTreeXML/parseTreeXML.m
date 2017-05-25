
function T = parseTreeXML(toParse,pathToFiles)


if nargin <2
pathToFiles = tempdir;
end

if nargin <1
    [toParse,pathToFiles] = uigetfile('*.xml','Select the NOAA-ITRDB XML file you want to parse')
end
    
if strncmp(toParse,'http://',7)
    %then it's a url, download it.
    q_dir=find(toParse=='/');
        fileName=toParse(q_dir(end)+1:end);
    ml_wget([pathToFiles fileName],toParse)
    toParse=fileName;
end
   
a=parseXML([pathToFiles toParse]);

% Get ID:
qID=find(strcmp(cellstr(char(a.Children.Name)),'Entry_ID'));
siteID=strrep(a.Children(qID).Children.Data,'-','_');
T.(siteID).Name=a.Children(find(strcmp(cellstr(char(a.Children.Name)),'Entry_Title'))).Children.Data;


% At a minimum, we need: 
% Lat (under Spatial_coverage)
qSpatialCoverage=find(strcmp(cellstr(char(a.Children.Name)),'Spatial_Coverage'));
qLat=find(strcmp(cellstr(char(a.Children(qSpatialCoverage).Children.Name)),'Southernmost_Latitude'));
T.(siteID).lat=eval(a.Children(qSpatialCoverage).Children(qLat).Children.Data);

% Lon
qLon=find(strcmp(cellstr(char(a.Children(qSpatialCoverage).Children.Name)),'Westernmost_Longitude'));
T.(siteID).lon=eval(a.Children(qSpatialCoverage).Children(qLon).Children.Data);

% Elevation
qElev=find(strcmp(cellstr(char(a.Children(qSpatialCoverage).Children.Name)),'Minimum_Altitude'));
T.(siteID).elev=eval(a.Children(qSpatialCoverage).Children(qElev).Children.Data);

% URL & file name
qRelatedURLs=find(strcmp(cellstr(char(a.Children.Name)),'Related_URL'));

% loop through "related urls" tag
count=1;
for i =1:length(qRelatedURLs);    
    qURLi=find(strcmp(cellstr(char(a.Children(qRelatedURLs(i)).Children.Name)),'URL'));
    
    % looop through URLs to find crns, 
    for  j=1:length(qURLi)
        url=a.Children(qRelatedURLs(i)).Children(qURLi(j)).Children.Data;
        q_dir=find(url=='/');
        fileName=url(q_dir(end)+1:end);
        recName=fileName(1:end-4);
        fileType= fileName(end-2:end);        
        
        % If no local copy exists, go get it:
        if ~exist([pathToFiles fileName])
            ml_wget([pathToFiles fileName],url)
        end

        %clear to make sure no leftovers from last loop
        clear x yr s X yrX nms Tvalid
        switch fileType
            case 'crn'
                [x,s,yr]=crn2vec2([pathToFiles fileName]);
                T.(siteID).(recName).chronology.filename=fileName;
                T.(siteID).(recName).chronology.url=url;
                T.(siteID).(recName).chronology.ID=recName;
                T.(siteID).(recName).chronology.Data=x;
                T.(siteID).(recName).chronology.Time=yr;
                T.(siteID).(recName).chronology.nSamp=s;                
                
            case 'rwl'
                [X,yrX,nms,Tvalid]=rwl2tsm([pathToFiles fileName]);
                T.(siteID).(recName).measurements.filename=fileName;
                T.(siteID).(recName).measurements.url=url;
                T.(siteID).(recName).measurements.ID=nms;
                T.(siteID).(recName).measurements.Data=X;
                T.(siteID).(recName).measurements.Time=yrX;
                T.(siteID).(recName).measurements.Tvalid=Tvalid;       
            case 'txt'
                T.(siteID).(recName).stats=fileread([pathToFiles fileName]);

                
        end
        count=count+1;
    end
        
end

