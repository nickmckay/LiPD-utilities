function [P,I]=readLiPD(lpdname)

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
if isunix
    cd([tempdir headerName '/data' ]);
else
    cd([tempdir headerName '\data' ]);
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

%assign in metadata MD5
I.metadataMD5=metaMD5;
I.tagMD5=tmd5;

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
torem={'paleoMD5','chronMeasMD5','chronEnsMD5','chronModelTableMD5'};
I=rmfieldsoft(I,torem);

%%%%%COMBINE TO CREATE FINAL
P=I;
P.paleoData=PD;
if isstruct(C)
P.chronData=C;
end

cd(p)
%end





