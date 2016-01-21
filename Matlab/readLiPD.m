function [P,I]=readLiPD(lpdname)
p=pwd;
slashi=union(strfind(lpdname,'/'),strfind(lpdname,'\') );
starti=max(union(0,slashi));
headerName=lpdname((starti+1):(end-4));
%display(lpdname)
unzip(lpdname,tempdir);
if isunix
    cd([tempdir headerName '/data' ]);
else
    cd([tempdir headerName '\data' ]);
end

filename=[headerName '.jsonld'];

%filename='Buckeye Creek..2008.jsonld';
%filename=[dnames(ii).name '.jsonld'];
%function P=loadPaleoArchive(filename);
I=loadjson(filename);

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

%load in geo information
I.geo.latitude=I.geo.geometry.coordinates(:,1);
I.geo.meanLat=nanmean(I.geo.latitude);
I.geo.longitude=I.geo.geometry.coordinates(:,2);
I.geo.meanLon=nanmean(I.geo.longitude);

%if theres elevation/depth, grab it too
if size(I.geo.geometry.coordinates,2)>2
    I.geo.elevation= I.geo.geometry.coordinates(:,3);
    I.geo.meanElev=mean(I.geo.elevation);
end

%bring property fields up a level
propFields=fieldnames(I.geo.properties);
for pf=1:length(propFields)
    I.geo.(propFields{pf})=I.geo.properties.(propFields{pf});
end

%remove properties and coordiantes structures
I.geo=rmfield(I.geo,{'properties','geometry'});

%%%%%%%END GEO SECTION %%%%%%%%%

%%%%%%%BEGIN PUB SECTION%%%%%%%%%%%
%pull DOI to front
if ~iscell(I.pub)
    clear pu
    pu{1}=I.pub;
    I.pub=pu;
end
for pp=1:length(I.pub)
    if isfield(I.pub{pp},'identifier')
        if strcmpi(I.pub{pp}.identifier{1,1}.type,'doi')
            I.pub{pp}.DOI=I.pub{pp}.identifier{1,1}.id;
        end
    end
end



%%%%%%%END PUB SECTION%%%%%%%%%%%

%quick fix rename measurments to paleoData
if isfield(I,'measurements') & ~isfield(I,'paleoData')
    I.paleoData=I.measurements;
end




tomt=1:length(I.paleoData);
%load in paleoDataTables
for i =tomt;
    mT=I.paleoData{i};
    %read in csv
    ncol=length(mT.columns);
    %try to read in as numeric data
    %[dirname mT.filename];
    
    if ~verLessThan('matlab','8.2')
        %use readtable! Requires matlab year > 14
        pdTable=table2cell(readtable([dirname mT.filename],'ReadVariableNames',0),'TreatAsEmpty','NA');
    else %try to do it the old way
        try
            pdTable=csvread([dirname mT.filename]);
        catch DO
            try%try to read in without header
                pdTable=csvread([dirname mT.filename],1,0);
            catch DO2
                %figure out which columns are string and float
                clear dataType
                for cc=1:length(mT.columns)
                    
                    if isfield(mT.columns{cc},'dataType')
                        if ~isempty(strfind(lower(mT.columns{cc}.dataType),'str')) | ~isempty(strfind(lower(mT.columns{cc}.dataType),'char'))
                            dataType{1,cc}='%s';
                        else
                            dataType{1,cc}='%f';
                        end
                    else %if not, guess that it's a string.
                        dataType{1,cc}='%s';
                        
                    end
                end
                
                fid=fopen([dirname mT.filename]);
                %[dirname mT.filename];
                %count how many columns
                line=fgetl(fid);
                ncolumn=length(strfind(line,','))+1;
                while ncolumn > length(dataType)
                    %add str columns to make it work
                    dataType=[dataType {'%s'}];
                end
                pdTable=textscan(fid,strjoin(dataType),'Delimiter',',','EndOfLine','\r');
                fclose(fid)
            end
        end
    end
    %check for same number of columns
    if length(mT.columns)~=size(pdTable,2)
        'WARNING - METADATA and DATA disagree on number of columns!!!!'
        'using minimum of the two'
        I.warnings='METADATA and DATA disagree on number of columns!!!!';
        ncol = min( [length(mT.columns),size(pdTable,2)]);
    end
    %now assign data to columns
    
    for j=1:ncol
        
        if iscell(pdTable)
            mT.columns{j}.values=pdTable(:,j);
            if iscell(mT.columns{j}.values);
                try  mT.columns{j}.values=cell2mat(mT.columns{j}.values);%try cell2mat
                catch DO3
                    try  mT.columns{j}.values=cell2num(mT.columns{j}.values);%try cell2num
                    catch DO4
                    end
                end
                if ischar(mT.columns{j}.values)
                    mT.columns{j}.values=cellstr(mT.columns{j}.values);
                end
            end
        else
            mT.columns{j}.values=pdTable(:,j);
        end
        %remove unneeded variables
        unneeded={'placeholder'};
        for un=1:length(unneeded)
            if isfield(mT.columns{j},unneeded{un})
                mT.columns{j}=rmfield(mT.columns{j},unneeded{un});
            end
        end
    end
    %remove unneeded variables
    mT=rmfield(mT,'filename');
    I.paleoData{i}=mT;
end

toct=NaN;
if isfield(I,'chronData')
    toct=1:length(I.chronData);
end

if ~isnan(toct) %if there are chron tables, load em in
    for i =toct;
        cT=I.chronData{i};
        %read in csv
        ncol=length(cT.columns);
        %try to read in as numeric data
        [dirname cT.filename];
        if ~verLessThan('matlab','8.2')
            %use readtable! Requires matlab year >= 13b
            pdTable=table2cell(readtable([dirname cT.filename],'ReadVariableNames',0),'TreatAsEmpty','NA');
        else
            try
                pdTable=csvread([dirname cT.filename]);
            catch DO
                try%try to read in without header
                    pdTable=csvread([dirname cT.filename],1,0);
                catch DO2
                    %figure out which columns are string and float
                    clear dataType
                    for cc=1:length(cT.columns)
                        if ~isempty(strfind(lower(cT.columns{cc}.dataType),'str'))
                            dataType{1,cc}='%s';
                        else
                            dataType{1,cc}='%f';
                        end
                    end
                    
                    fid=fopen([dirname cT.filename]);
                    [dirname cT.filename]
                    %count how many columns
                    line=fgetl(fid);
                    ncolumn=length(strfind(line,','))+1;
                    while ncolumn > length(dataType)
                        %add str columns to make it work
                        dataType=[dataType {'%s'}];
                    end
                    pdTable=textscan(fid,[strjoin(dataType)],'Delimiter',',','EndOfLine','\n');
                    fclose(fid)
                end
            end
        end
        
        %check for same number of columns
        if length(cT.columns)~=size(pdTable,2)
            'WARNING - METADATA and DATA disagree on number of columns!!!!'
            'using minimum of the two'
            I.warnings='METADATA and DATA disagree on number of columns!!!!';
            ncol = min( [length(cT.columns),size(pdTable,2)]);
        end
        %now assign data to columns
        
        for j=1:ncol
            
            if iscell(pdTable)
                cT.columns{j}.values=pdTable{:,j};
                if iscell(cT.columns{j}.values);
                    try  cT.columns{j}.values=cell2num(cT.columns{j}.values);
                    catch DO3
                        try  cT.columns{j}.values=cell2mat(cT.columns{j}.values);
                        catch DO4
                        end
                        
                    end
                end
            else
                cT.columns{j}.values=pdTable(:,j);
            end
        end
        I.chronData{i}=cT;
    end
end

%convert cells to structures
P=I;
%paleodata
clear NS
for i=tomt
    for j=1:length(I.paleoData{i}.columns)
        %quick fix rename parameter to variableName
        if isfield(I.paleoData{i}.columns{j},'parameter') & ~isfield(I.paleoData{i}.columns{j},'variableName')
            I.paleoData{i}.columns{j}.variableName=I.paleoData{i}.columns{j}.parameter;
            I.paleoData{i}.columns{j}=rmfield(I.paleoData{i}.columns{j},'parameter');
        end
        newname=genvarname(I.paleoData{i}.columns{j}.variableName,fieldnames(P.paleoData{i}));
        P.paleoData{i}.(newname)=I.paleoData{i}.columns{j};
    end
    NS.(genvarname(P.paleoData{i}.paleoDataTableName))=P.paleoData{i};
    NS.(genvarname(P.paleoData{i}.paleoDataTableName))=rmfield(NS.(genvarname(P.paleoData{i}.paleoDataTableName)),'columns');
end
P.paleoData=NS;
%chron
clear NS
if ~isnan(toct)
    for i=toct
        for j=1:length(I.chronData{i}.columns)
            newname=genvarname(I.chronData{i}.columns{j}.variableName,fieldnames(P.chronData{i}));
            P.chronData{i}.(newname)=I.chronData{i}.columns{j};
        end
        NS.(genvarname(P.chronData{i}.chronDataTableName))=P.chronData{i};
        NS.(genvarname(P.chronData{i}.chronDataTableName))=rmfield(NS.(genvarname(P.chronData{i}.chronDataTableName)),'columns');
    end
    P.chronData=NS;
end
cd(p)
%end





