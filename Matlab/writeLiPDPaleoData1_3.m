function LiPDStruct = writeLiPDPaleoData1_2(LiPDStruct,goodOutName,writeDistributionTable,pdlev)
if nargin<3
    writeDistributionTable=1;
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


%%%%%%%paleoDATA SECTION%%%%%%%
%build data tables then write out
%first data tables, and write data table names intp structure
if isfield(LiPDStruct,'paleoData')
    %loop through all the paleoologies
    for chr=1:length(LiPDStruct.paleoData)
        
        %%%%% BEGIN - paleo MEASUREMENT TABLE
        %if there is a measurementTable, write it out
        if isfield(LiPDStruct.paleoData{chr},'measurementTable')
            for cmt=1:length(LiPDStruct.paleoData{chr}.measurementTable)
                DT=LiPDStruct.paleoData{chr}.measurementTable{cmt};
                colnames=structFieldNames(DT);
                
                if ~isfield(DT,'measurementTableName')
                    DT.measurementTableName=['measurementTable' num2str(cmt)];
                end
                if length(colnames)<1
                    error('There don''t seem to be enough columns in this data table')
                end
                clear outTable
                cN=0;
                for c=1:length(colnames)
                    if isstruct(DT.(colnames{c})) %ignore non structure components
                        if ~isfield(DT.(colnames{c}),'values')
                            warnings=[warnings {warning('No values field in structure, this shouldn''t be')}];
                        else
                            if ~isfield(DT.(colnames{c}),'variableName')
                                DT.(colnames{c}).variableName=colnames{c};
                            end
                            cN=cN(end)+(1:size(DT.(colnames{c}).values,2));
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
                csvname=[goodOutName '.paleo' num2str(chr) '.' DT.measurementTableName '.csv'];
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
                
                NLS{cmt}=DT;
            end
            LiPDStruct.paleoData{chr}.measurementTable=NLS;
            
        end
        %%%%% END - paleo MEASUREMENT TABLE
        
        %%%%% Start - paleo MODEL
        
        %if there is a model section, write it out
        if isfield(LiPDStruct.paleoData{chr},'model')
            
            for cm = 1:length(LiPDStruct.paleoData{chr}.model)
                %%%%%% BEGIN -  paleo Model Table (Summary output).
                if isfield(LiPDStruct.paleoData{chr}.model{cm},'summaryTable')
                    for pst = 1:length(LiPDStruct.paleoData{chr}.model{cm}.summaryTable)
                        DT=LiPDStruct.paleoData{chr}.model{cm}.summaryTable{pst};
                        colnames=structFieldNames(DT);
                        
                        
                        if length(colnames)<1
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
                                    cN=cN(end)+(1:size(DT.(colnames{c}).values,2));
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
                        csvname=[goodOutName '.paleo' num2str(chr) '.Model' num2str(cm) '.summaryTable' num2str(pst) '.csv'];
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
                        
                        LiPDStruct.paleoData{chr}.model{cm}.summaryTable{pst}=DT;
                    end
                end
                %%%%%% END -  paleo Model Table (Summary output).
                %%%%%% BEGIN -  paleo Ensemble Table
                if isfield(LiPDStruct.paleoData{chr}.model{cm},'ensembleTable')
                    for pet = 1:length(LiPDStruct.paleoData{chr}.model{cm}.ensembleTable)
                        DT=LiPDStruct.paleoData{chr}.model{cm}.ensembleTable{pet};
                        colnames=structFieldNames(DT);
                        if length(colnames)<1
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
                                    cN=cN(end)+(1:size(DT.(colnames{c}).values,2));
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
                        csvname=[goodOutName '.paleo' num2str(chr) '.Model' num2str(cm) '.EnsembleTable' num2str(pet) '.csv'];
                        DT.filename=csvname;
                        
                        
                        csvwrite(csvname,outTable);
                        
                        
                        LiPDStruct.paleoData{chr}.model{cm}.ensembleTable{pet}=DT;
                    end
                    %%%%%% END -  paleo Ensemble Table
                end
                %%%%%% BEGIN -  probability distribution table
                if isfield(LiPDStruct.paleoData{chr}.model{cm},'distributionTable')
                    %loop through all the ages
                    for ca = 1:length(LiPDStruct.paleoData{chr}.model{cm}.distributionTable)
                        DT = LiPDStruct.paleoData{chr}.model{cm}.distributionTable{ca};
                        colnames=structFieldNames(DT);
                        
                        
                        %I don't think it needs a name anymore
                        %DT.paleoTableName=mnames{m};
                        if length(colnames)<1
                            error('There don''t seem to be enough columns in this data table')
                        end
                        clear outTable
                        cN=0;
                        for c=1:length(colnames)
                            if ~isfield(DT.(colnames{c}),'values')
                                warnings=[warnings {warning('No values field in structure, this shouldn''t be')}];
                            else
                                if writeDistributionTable
                                    DT.(colnames{c}).variableName=colnames{c};
                                    cN=cN(end)+(1:size(DT.(colnames{c}).values,2));
                                    DT.(colnames{c}).number=cN;
                                    if iscell(DT.(colnames{c}).values)
                                        error('distrubtion data need to have only matrices, not cells')
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
                        if writeDistributionTable
                            csvname=[goodOutName '.paleo' num2str(chr) '.Model' num2str(cm) '.distributionTable.' num2str(ca) '.csv'];
                            DT.filename=csvname;
                            if filterProbDens%remove very small probabilities
                                csvwrite(csvname,outTable(hipd,:));
                                
                            else
                                csvwrite(csvname,outTable);
                            end
                        end
                        LiPDStruct.paleoData{chr}.model{cm}.distributionTable{ca} =DT;
                        
                    end
                end
                %%%%%% END -  Calibrated Age Data
                
                
            end
        end
    end
end

