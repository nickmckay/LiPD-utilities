function [P,I,C]=readLiPD(lpdname)

%ui selection
if nargin<1
    [lpdfile, lpdpath] = uigetfile('.lpd');
    lpdname = [lpdpath lpdfile];
end



%deal with slashes and location
p=pwd;
slashi=union(strfind(lpdname,'/'),strfind(lpdname,'\') );
starti=max(union(0,slashi));
headerName=lpdname((starti+1):(end-4));
display(['Reading ' headerName '.lpd ...'])

%unzip the bagged file
unzip(lpdname,tempdir);


%check for bagging...

if isunix
    if isdir([tempdir headerName '/data' ])%it's bagged!
        bagged=1;
        cd([tempdir headerName '/data' ]);
    else%it's not! %Don't worry - we'll get it next time.
        cd([tempdir headerName ]);
        bagged=0;
    end
    
else
    if isdir([tempdir headerName '\data' ])%it's bagged!
        bagged=1;
        cd([tempdir headerName '\data' ]);
    else%it's not! %Don't worry - we'll get it next time.
        cd([tempdir headerName ]);
        bagged=0;
    end
end

filename=[headerName '.jsonld'];


I=loadjson(filename);

%%%% Deal with versioning
if isfield(I,'LiPDVersion')
    vers=I.LiPDVersion;
    if ischar(vers)
        vers=str2num(vers);
    end
else
    vers = 1.0;
end
I.LiPDVersion = vers;
%load in version information
assignSubcomponentVersions;

wvi=find(vers==cell2mat(vi(:,1)));
if isempty(wvi)
    warning(['Version not recognized, using version ' num2str(vi{end,1})])
    wvi=size(vi,1);
end

V=vi{wvi,2};




%get MD5 sums from bag
eval(['grabMD5s' V.MD5v])

    
   %look for directories
if isunix
    slashfind=strfind(filename,'/');
elseif ispc
    slashfind=strfind(filename,'\');
end

%get directory name
lsl=length(slashfind);
if lsl>0
    dirname=filename(1:slashfind(lsl));
else
    if isunix
        dirname=[pwd '/'];
    elseif ispc
        dirname=[pwd '\'];
    end
end
tomt=NaN;
toct=NaN;

if isfield(I,'x0x40_context')
    I=rmfield(I,'x0x40_context');
end



%%%%BEGIN GEO SECTION %%%%%%%%%%%%%%%
eval(['I = readLiPDGeo' V.geov '(I);']);
%%%%%%%END GEO SECTION %%%%%%%%%

%%%%%%%BEGIN PUB SECTION%%%%%%%%%%%
eval(['I = readLiPDPub' V.pubv '(I);']);

%%%%%%%END PUB SECTION%%%%%%%%%%%

%deprecated
% %quick fix rename measurments to paleoData
% if isfield(I,'measurements') & ~isfield(I,'paleoData')
%     I.paleoData=I.measurements;
% end

%%%%%%%BEGIN PALEODATA SECTION%%%%%%%%%%%
eval(['PD = readLiPDPaleoData' V.paleoDatav '(I,dirname);']);
%%%%%%%END PALEODATA SECTION%%%%%%%%%%%

%%%%%%%BEGIN CHRONDATA SECTION%%%%%%%%%%%

eval(['C = readLiPDChronData' V.chronDatav '(I,dirname);']);
%%%%%%%END CHRONDATA SECTION%%%%%%%%%%%


%remove unneeded variables from top structure
torem={'paleoMD5','chronMeasMD5','chronEnsMD5','chronSummaryTableMD5','paleoMeasMD5','paleoEnsMD5','paleoSummaryTableMD5'};
I=rmfieldsoft(I,torem);

%%%%%COMBINE TO CREATE FINAL
P=I;
P.paleoData=PD;

if iscell(C) | isstruct(C)
    P.chronData=C;
end

cd(p)
rmdir([tempdir headerName],'s');


%%%%%UPDATE TO MOST RECENT VERSION
P=convertLiPD1_0to1_1(P);
P=convertLiPD1_1to1_2(P);


%end





