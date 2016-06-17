
function writeLiPD(LiPDStruct,bagit,outdir)
load LiPDUtilitiesPreferences.mat
LiPDVersion = '1.2';
LiPDStruct.LiPDVersion = LiPDVersion;
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
goodOutName=regexprep(LiPDStruct.dataSetName,'[^a-zA-Z0-9-.]','');
display(goodOutName)
%goodOutName(ismember(goodOutName,'!,;:/\|*~.')) = [];
%goodOutName=makeValidName(goodOutName);

if ~isdir([outdir goodOutName])
    mkdir([outdir goodOutName])
end

cd([outdir goodOutName])

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
jout=savejsonld('',LiPDStruct,[goodOutName '.jsonld']);

%fix unicode issues
if isunix
    fixUnicodeFile([goodOutName '.jsonld'])
end

if bagit
    
    %2. bagit
    system([githubPath '/bagit.py  ' outdir '/' goodOutName])
    
    %3. compress it and rename it
    system(['cd ' outdir '; zip -r ' outdir goodOutName '.lpd ' goodOutName]);
    system(['cp ' outdir goodOutName '.lpd ' writedir '/']);
    rmdir([outdir goodOutName],'s');

end
cd(curdir);




