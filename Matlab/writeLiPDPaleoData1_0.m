function LiPDStruct = writeLiPDPaleoData1_1(LiPDStruct,goodOutName)

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
                if ~isfield(DT.(colnames{c}),'variableName')
                    warning('No variable name, using structure name')
                    DT.(colnames{c}).variableName=colnames{c};
                end
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
