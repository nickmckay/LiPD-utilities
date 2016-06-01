function LiPDStruct = writeLiPDChronData1_1(LiPDStruct,goodOutName,writeCalAges,pdlev)
if nargin<3
    writeCalAges=0;
end
if nargin<4
    pdlev=1e-6;
    filterProbDens=1;
else
    if pdlev>0
        filterProbDens=1;
    else
        filterProbDens=0;
    end
end


%%%%%%%CHRONDATA SECTION%%%%%%%
%build data tables then write out
%first data tables, and write data table names intp structure
if isfield(LiPDStruct,'chronData')
    %loop through all the chronologies
    for chr=1:length(LiPDStruct.chronData)
        
        %%%%% BEGIN - CHRON MEASUREMENT TABLE
        %if there is a chronMeasurementTable, write it out
        if isfield(LiPDStruct.chronData{chr},'chronMeasurementTable')
            
            DT=LiPDStruct.chronData{chr}.chronMeasurementTable;
            colnames=fieldnames(DT);
            clear keep
            for k=1:length(colnames)
                keep(k)=isstruct(DT.(colnames{k}));
            end
            colnames=colnames(find(keep));
            
            %I don't think it needs a name anymore
            %DT.chronTableName=mnames{m};
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
            csvname=[goodOutName '.Chron' num2str(chr) '.ChronMeasurementTable.csv'];
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
            
            %there should only be one I think.
            %             if m~=1
            %                 error('there should only be one chronMeasurementTable per chronology')
            %             end
            NLS.chronData=DT;
            
            %                 if m==1
            %                     NLS.chronData={DT};
            %                 else
            %                     NLS.chronData(m,1)={DT};
            %                 end
        end
        LiPDStruct.chronData{chr}.chronMeasurementTable=NLS.chronData;
        %%%%% END - CHRON MEASUREMENT TABLE
        
        %%%%% Start - CHRON MODEL
        
        %if there is a chronModel section, write it out
        if isfield(LiPDStruct.chronData{chr},'chronModel')
            
            for cm = 1:length(LiPDStruct.chronData{chr}.chronModel)
                %%%%%% BEGIN -  Chron Model Table (Summary output).
                if isfield(LiPDStruct.chronData{chr}.chronModel{cm},'chronModelTable')
                    DT=LiPDStruct.chronData{chr}.chronModel{cm}.chronModelTable;
                    colnames=fieldnames(DT);
                    clear keep
                    for k=1:length(colnames)
                        keep(k)=isstruct(DT.(colnames{k}));
                    end
                    colnames=colnames(find(keep));
                    
                    %I don't think it needs a name anymore
                    %DT.chronTableName=mnames{m};
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
                    csvname=[goodOutName '.Chron' num2str(chr) '.Model' num2str(cm) '.ChronModelTable.csv'];
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
                    
                    %there should only be one I think.
                    %                     if m~=1
                    %                         error('there should only be one chronMeasurementTable per chronology')
                    %                     end
                    NLS.chronData=DT;
                    
                    %                 if m==1
                    %                     NLS.chronData={DT};
                    %                 else
                    %                     NLS.chronData(m,1)={DT};
                    %                 end
                    
                    LiPDStruct.chronData{chr}.chronModel{cm}.chronModelTable=NLS.chronData;
                end
                %%%%%% END -  Chron Model Table (Summary output).
                %%%%%% BEGIN -  Chron Ensemble Table
                if isfield(LiPDStruct.chronData{chr}.chronModel{cm},'ensembleTable')
                    DT=LiPDStruct.chronData{chr}.chronModel{cm}.ensembleTable;
                    colnames=fieldnames(DT);
                    clear keep
                    for k=1:length(colnames)
                        keep(k)=isstruct(DT.(colnames{k}));
                    end
                    colnames=colnames(find(keep));
                    
                    %I don't think it needs a name anymore
                    %DT.chronTableName=mnames{m};
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
                                cN=cN+(1:size(DT.(colnames{c}).values,2));
                                DT.(colnames{c}).number=cN;
                                  if iscell(DT.(colnames{c}).values)
                                        error('Ensemble Tables need to number only matrices, not cells')
                                  end
                                  if exist('outTable')                                  
                                      outTable=[outTable DT.(colnames{c}).values];
                                  else                                      
                                      outTable=DT.(colnames{c}).values;
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
                    csvname=[goodOutName '.Chron' num2str(chr) '.Model' num2str(cm) '.EnsembleTable.csv'];
                    DT.filename=csvname;
                    

                       csvwrite(csvname,outTable);


                    LiPDStruct.chronData{chr}.chronModel{cm}.ensembleTable=DT;
                    %%%%%% END -  Chron Ensemble Table
                end
                %%%%%% BEGIN -  Calibrated Age Data
                if isfield(LiPDStruct.chronData{chr}.chronModel{cm},'calibratedAges')
                    %loop through all the ages
                    for ca = 1:length(LiPDStruct.chronData{chr}.chronModel{cm}.calibratedAges)
                        DT = LiPDStruct.chronData{chr}.chronModel{cm}.calibratedAges{ca};
                        colnames=structFieldNames(DT);
                        
                        
                        %I don't think it needs a name anymore
                        %DT.chronTableName=mnames{m};
                        if length(colnames)<2
                            error('There don''t seem to be enough columns in this data table')
                        end
                        clear outTable
                        cN=0;
                        for c=1:length(colnames)
                            if ~isfield(DT.(colnames{c}),'values')
                                warnings=[warnings {warning('No values field in structure, this shouldn''t be')}];
                            else
                                if writeCalAges
                                    DT.(colnames{c}).variableName=colnames{c};
                                    cN=cN+(1:size(DT.(colnames{c}).values,2));
                                    DT.(colnames{c}).number=cN;
                                    if iscell(DT.(colnames{c}).values)
                                        error('Calibrated age data need to number only matrices, not cells')
                                    end
                                    if exist('outTable')
                                        outTable=[outTable DT.(colnames{c}).values];
                                    else
                                        outTable=DT.(colnames{c}).values;
                                    end
                                    if filterProbDens
                                        if strcmp(colnames{c},'probabilityDensity')
                                            hipd=find(DT.(colnames{c}).values >= pdlev);
                                        end
                                    end
                                end
                                DT.(colnames{c})=rmfield(DT.(colnames{c}),'values');
                            end
                            %put column in "columns" set,
                            if c==1
                                DT.columns={DT.(colnames{c})};
                            else
                                DT.columns(c,1)={DT.(colnames{c})};
                            end
                            DT=rmfield(DT,colnames{c});
                        end
                        if writeCalAges
                            csvname=[goodOutName '.Chron' num2str(chr) '.Model' num2str(cm) '.calibratedAge.' num2str(ca) '.csv'];
                            DT.filename=csvname;
                            if filterProbDens%remove very small probabilities
                                csvwrite(csvname,outTable(hipd,:));
                                
                            else
                                csvwrite(csvname,outTable);
                            end
                        end
                        LiPDStruct.chronData{chr}.chronModel{cm}.calibratedAges{ca} =DT;
                        
                    end
                end
                %%%%%% END -  Calibrated Age Data
                
                
            end
        end
    end
end

