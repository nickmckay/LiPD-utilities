
function writeLiPDFile(LiPDStruct,outdir)
load LiPDUtilitiesPreferences.mat

if isfield(LiPDStruct,'LiPDVersion') & ~isfield(LiPDStruct,'lipdVersion')
    lipdVersion = LiPDStruct.LiPDVersion;
    LiPDStruct.lipdVersion = lipdVersion;
end

if ~isfield(LiPDStruct,'lipdVersion')
    lipdVersion = 1.3;
    LiPDStruct.lipdVersion = lipdVersion;
end
 LiPDStruct = rmfieldsoft(LiPDStruct,'LiPDVersion');


LiPDStruct.createdBy = 'matlab';


%LiPD exporter
curdir=pwd;


if nargin<2
    writedir=pwd;
else
    writedir=outdir;
end

outdir=[tempdir 'lpdTemp/'];
if isdir(outdir);
    rmdir(outdir,'s');
end





warnings={};
%Overwrite option?
%first create new folder for the record if need be
goodDirName='bag';
goodOutName=regexprep(LiPDStruct.dataSetName,'[^a-zA-Z0-9-.]','');


if ~isdir([outdir goodDirName])
    mkdir([outdir goodDirName])
end

cd([outdir goodDirName])

%%%%%Write GEO SECTION %%%%%%%%%%
LiPDStruct = writeLiPDGeo1_0(LiPDStruct);


%%%%%Write PUB SECTION %%%%%%%%%%
LiPDStruct = writeLiPDPub1_0(LiPDStruct);

%%%%%Write Paleodata SECTION%%%%%%%
LiPDStruct = writeLiPDPaleoData1_3(LiPDStruct,goodOutName);

%%%%%Write Chrondata SECTION%%%%%%%
LiPDStruct = writeLiPDChronData1_3(LiPDStruct,goodOutName,1);


%%%%%%Remove unneeded fields
torem = {'paleoMD5','chronMeasMD5','chronEnsMD5','chronModelTableMD5','chronMD5','warnings',...
    'metadataMD5'};

LiPDStruct = rmfieldsoft(LiPDStruct,torem);



%Write files out
%1. write into directory
jout=savejsonld('',LiPDStruct,'metadata.jsonld');

%fix unicode issues
if isunix
    fixUnicodeFile(['metadata.jsonld'])
end

if isunix
    %2. bagit
    system([githubPath '/bagit.py  ' outdir '/bag'])
    
    %3. compress it and rename it
    system(['cd ' outdir '; zip -r ' outdir goodOutName '.lpd ' goodDirName]);
    system(['cp ' outdir goodOutName '.lpd ' writedir '/']);
    rmdir([outdir goodDirName],'s');
else
    error('write functionality is not yet supported on windows')
end



cd(curdir);




