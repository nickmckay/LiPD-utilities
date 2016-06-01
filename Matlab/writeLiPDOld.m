
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
%goodOutName=makeValidName(goodOutName);

if ~isdir([outdir goodOutName])
    mkdir([outdir goodOutName])
end

cd([outdir goodOutName])

%%%%%BEGIN GEO SECTION %%%%%%%%%%
LiPDStruct = writeLiPDGeo1_0_0(LiPDStruct);
%%%%%END GEO SECTION %%%%%%%%%%


%%%%%START PUB SECTION %%%%%%%%%%
LiPDStruct = writeLiPDPub1_0_0(LiPDStruct);

%%%%%END PUB SECTION %%%%%%%%%%


%%%%%%%PALEODATA SECTION%%%%%%%
LiPDStruct = writeLiPDPub1_0_0(LiPDStruct);


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
                    DT.(colnames{c}).variableName=colnames{c};
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




%Write files out
%1. write into directory
jout=savejsonld('',LiPDStruct,[goodOutName '.jsonld']);

%fix unicode issues
if isunix
    fixUnicodeFile([goodOutName '.jsonld'])
end

if bagit
    
    %2. bagit
    system(['/Library/Frameworks/Python.framework/Versions/3.4/bin/bagit.py  ' outdir '/' goodOutName])
    
    %3. compress it and rename it
    system(['cd ' outdir '; zip -r ' outdir goodOutName '.lpd ' goodOutName]);
    system(['cp ' outdir goodOutName '.lpd ' writedir '/']);
end
cd(curdir);



