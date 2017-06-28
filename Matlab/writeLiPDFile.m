
function writeLiPDFile(LiPDStruct,bagit,outdir)
load LiPDUtilitiesPreferences.mat
LiPDVersion = '1.3';
LiPDStruct.LiPDVersion = LiPDVersion;
LiPDStruct.createdBy = 'matlab';


%LiPD exporter
curdir=pwd;
if nargin<2
    bagit=1;
end

if bagit
    if nargin<3
        writedir=pwd;
    else
        writedir=outdir;
    end
    outdir=[tempdir 'lpdTemp/'];
    if isdir(outdir);
    rmdir(outdir,'s');
    end
elseif nargin<3
    outdir='~/Dropbox/LiPD/library/';
    % elseif ~strcmp(outdir(end),'/')
    %     outdir=[outdir '/'];
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
LiPDStruct = writeLiPDPaleoData1_2(LiPDStruct,goodOutName);

%%%%%Write Chrondata SECTION%%%%%%%
LiPDStruct = writeLiPDChronData1_2(LiPDStruct,goodOutName,1);


%%%%%%Remove unneeded fields
torem = {'paleoMD5','chronMeasMD5','chronEnsMD5','chronModelTableMD5','chronMD5','warnings'};

LiPDStruct = rmfieldsoft(LiPDStruct,torem);



%Write files out
%1. write into directory
jout=savejsonld('',LiPDStruct,'metadata.jsonld');

%fix unicode issues
if isunix
    fixUnicodeFile(['metadata.jsonld'])
end

if bagit
    
    %2. bagit
    system([githubPath '/bagit.py  ' outdir '/bag'])
    
    %3. compress it and rename it
    system(['cd ' outdir '; zip -r ' outdir goodOutName '.lpd ' goodDirName]);
    system(['cp ' outdir goodOutName '.lpd ' writedir '/']);
    rmdir([outdir goodDirName],'s');

end

cd(curdir);




