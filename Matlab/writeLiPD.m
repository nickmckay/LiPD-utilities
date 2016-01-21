
function writeLiPD(LiPDStruct,bagit,outdir)
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
%goodOutName=matlab.lang.makeValidName(goodOutName);

if ~isdir([outdir goodOutName])
    mkdir([outdir goodOutName])
end

cd([outdir goodOutName])

%%%%%BEGIN GEO SECTION %%%%%%%%%%
%check for latitude and longitude
if isfield(LiPDStruct.geo,'meanLat') & ~isfield(LiPDStruct.geo,'latitude')
    LiPDStruct.geo.latitude=LiPDStruct.geo.meanLat;
end
if isfield(LiPDStruct.geo,'meanLon') & ~isfield(LiPDStruct.geo,'longitude')
    LiPDStruct.geo.longitude=LiPDStruct.geo.meanLon;
end


%write coordinates back into geometry
if isfield(LiPDStruct.geo,'elevation')
    if isstruct(LiPDStruct.geo.elevation)
        if length(LiPDStruct.geo.elevation.value)~=length(LiPDStruct.geo.latitude)
            LiPDStruct.geo.geometry.coordinates=[LiPDStruct.geo.latitude LiPDStruct.geo.longitude repmat(LiPDStruct.geo.elevation.value,length(LiPDStruct.geo.latitude),1)];
        else
            LiPDStruct.geo.geometry.coordinates=[LiPDStruct.geo.latitude LiPDStruct.geo.longitude LiPDStruct.geo.elevation.value];
        end
        
    else
        if length(LiPDStruct.geo.elevation)~=length(LiPDStruct.geo.latitude)
            LiPDStruct.geo.geometry.coordinates=[LiPDStruct.geo.latitude LiPDStruct.geo.longitude repmat(LiPDStruct.geo.elevation,length(LiPDStruct.geo.latitude),1)];
        else
            LiPDStruct.geo.geometry.coordinates=[LiPDStruct.geo.latitude LiPDStruct.geo.longitude LiPDStruct.geo.elevation.value];
        end
    end
else
    LiPDStruct.geo.geometry.coordinates=[LiPDStruct.geo.latitude LiPDStruct.geo.longitude];
end

%write string properties into properties
gs=fieldnames(LiPDStruct.geo);
for s=1:length(gs)
    if ischar(LiPDStruct.geo.(gs{s})) & ~strcmp(gs{s},'type')
        LiPDStruct.geo.properties.(gs{s})=LiPDStruct.geo.(gs{s});
    end
end

%all geo objects should be features
LiPDStruct.geo.type='Feature';

%clean up fields that shouldn't be there
goodGeo={'type','geometry','properties'};
for s=1:length(gs)
    if ~strcmp(gs{s},goodGeo)
        LiPDStruct.geo=rmfield(LiPDStruct.geo,gs{s});
    end
end

%%%%%END GEO SECTION %%%%%%%%%%
%%%%%START PUB SECTION %%%%%%%%%%
for dd=1:length(LiPDStruct.pub)
    if isfield(LiPDStruct.pub{dd},'DOI')
        if iscell(LiPDStruct.pub{dd}.DOI)
            LiPDStruct.pub{dd}.DOI=LiPDStruct.pub{dd}.DOI{1};
        end
        doistring=strtrim(LiPDStruct.pub{dd}.DOI);
        dh=strfind(doistring,'doi:');
        if ~isempty(dh)                
            doistring=doistring(setdiff(1:length(doistring),dh));
        end
        LiPDStruct.pub{dd}.identifier{1,1}.type='doi';
        LiPDStruct.pub{dd}.identifier{1,1}.id=doistring;
        LiPDStruct.pub{dd}.identifier{1,1}.url=['http://dx.doi.org/' doistring];
        LiPDStruct.pub{dd}=rmfield(LiPDStruct.pub{dd},'DOI');
    end
end
%%%%%END PUB SECTION %%%%%%%%%%


%%%%%%%PALEODATA SECTION%%%%%%%
%build data tables then write out
%first data tables, and write data table names intp structure
mnames=fieldnames(LiPDStruct.paleoData);
for m=1:length(mnames)
    DT=LiPDStruct.paleoData.(mnames{m});
    colnames=fieldnames(DT);
    clear keep
    for k=1:length(colnames)
        keep(k)=isstruct(DT.(colnames{k}));
    end
    colnames=colnames(find(keep));
    DT.paleoDataTableName=mnames{m};
    if length(colnames)<2
        error('There don''t seem to be enough columns in this data table')
    end
    clear outTable
    cN=0;
    for c=1:length(colnames)
        if isstruct(DT.(colnames{c})) %ignore non structure components
            %remove fields that don't need to be written out
            toremf={'column','number'};
            for trf=1:length(toremf)
                if isfield(DT.(colnames{c}),toremf{trf})
                    DT.(colnames{c})=rmfield(DT.(colnames{c}),toremf{trf});
                end
            end
            if ~isfield(DT.(colnames{c}),'values')
                warnings=[warnings {warning('No values field in structure, this shouldn''t be')}];
            else
                if size(DT.(colnames{c}).values,1)==1
                    DT.(colnames{c}).values=DT.(colnames{c}).values';
                end
                DT.(colnames{c}).parameter=colnames{c};
                cN=cN+1;
                DT.(colnames{c}).number=cN;
                if exist('outTable')
                    if iscell(DT.(colnames{c}).values)
                        outTable=[outTable DT.(colnames{c}).values];
                    else
                        outTable=[outTable num2cell(DT.(colnames{c}).values)];
                    end
                else
                    if iscell(DT.(colnames{c}).values)
                        outTable=[DT.(colnames{c}).values];
                    else
                        outTable=num2cell(DT.(colnames{c}).values);
                    end
                end
                DT.(colnames{c})=rmfield(DT.(colnames{c}),'values');
            end
        end
        %put column in "columns" set,
        if c==1
            DT.columns={DT.(colnames{c})};
        else
            DT.columns(c,1)={DT.(colnames{c})};
        end
        DT=rmfield(DT,colnames{c});
    end
    csvname=[goodOutName '.' mnames{m} '.PaleoData.csv'];
    DT.filename=csvname;
    
    
    %deal with char cell problem
    for ii=1:size(outTable,1)
        for jj=1:size(outTable,2)
            dum=cell2str(outTable{ii,jj});
            dum(ismember(dum,''',')) = [];
            dum=strtrim(dum);
            outTable{ii,jj}=cellstr(char(dum));
        end
    end
    cell2csv(csvname,outTable);
    
    if m==1
        NLS.paleoData={DT};
    else
        NLS.paleoData(m,1)={DT};
    end
end
LiPDStruct.paleoData=NLS.paleoData;

%repeat for Chronology
if isfield(LiPDStruct,'chronData')
    mnames=fieldnames(LiPDStruct.chronData);
    for m=1:length(mnames)
        DT=LiPDStruct.chronData.(mnames{m});
        colnames=fieldnames(DT);
        clear keep
        for k=1:length(colnames)
            keep(k)=isstruct(DT.(colnames{k}));
        end
        colnames=colnames(find(keep));
        
        DT.chronTableName=mnames{m};
        if length(colnames)<2
            error('There don''t seem to be enough columns in this data table')
        end
        clear outTable
        cN=0;
        for c=1:length(colnames)
            if isstruct(DT.(colnames{c})) %ignore non structure components
                if ~isfield(DT.(colnames{c}),'values')
                    warnings=[warnings {warning('No values field in structure, this shouldn''t be')}];
                else
                    DT.(colnames{c}).parameter=colnames{c};
                    cN=cN+1;
                    DT.(colnames{c}).number=cN;
                    if exist('outTable')
                        if iscell(DT.(colnames{c}).values)
                            outTable=[outTable DT.(colnames{c}).values];
                        else
                            outTable=[outTable num2cell(DT.(colnames{c}).values)];
                        end
                    else
                        if iscell(DT.(colnames{c}).values)
                            outTable=[DT.(colnames{c}).values];
                        else
                            outTable=num2cell(DT.(colnames{c}).values);
                        end
                    end
                    DT.(colnames{c})=rmfield(DT.(colnames{c}),'values');
                end
            end
            %put column in "columns" set,
            if c==1
                DT.columns={DT.(colnames{c})};
            else
                DT.columns(c,1)={DT.(colnames{c})};
            end
            DT=rmfield(DT,colnames{c});
        end
        csvname=[goodOutName '.' mnames{m} '.ChronTable.csv'];
        DT.filename=csvname;
        
        %deal with char cell problem
        for ii=1:size(outTable,1)
            for jj=1:size(outTable,2)
                dum=cell2str(outTable{ii,jj});
                dum(ismember(dum,''',')) = [];
                dum=strtrim(dum);
                outTable{ii,jj}=cellstr(char(dum));
            end
        end
        cell2csv(csvname,outTable);
        
        if m==1
            NLS.chronData={DT};
        else
            NLS.chronData(m,1)={DT};
        end
    end
    LiPDStruct.chronData=NLS.chronData;
end



%
%write out lipd file
%1. write into directory
jout=savejsonld('',LiPDStruct,[goodOutName '.jsonld']);

if bagit
    
    %2. bagit
    system(['/Library/Frameworks/Python.framework/Versions/3.4/bin/bagit.py  ' outdir '/' goodOutName])
    
    %3. compress it and rename it
    system(['cd ' outdir '; zip -r ' outdir goodOutName '.lpd ' goodOutName]);
    system(['cp ' outdir goodOutName '.lpd ' writedir '/']);
end
cd(curdir);



