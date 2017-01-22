function C=readLiPDChronData1_2(I,dirname)


toct=NaN;
if isfield(I,'chronData')
    C=I.chronData;
    toct=1:length(I.chronData);
end



if ~isnan(toct) %if there are chron tables, load em in
    for i = toct; %go through each chronology
        %%%%%CHRON MEASUREMENT TABLE
        
        %Go through chronMeasurementTable first
        for cmt=1:length(I.chronData{i}.chronMeasurementTable)
        cT = I.chronData{i}.chronMeasurementTable{cmt};
        
        cT=readLiPDTable(cT,dirname);
        cT=processLiPDColumns(cT);
        if size(I.chronMeasMD5,1)>=i    
            if iscell(I.chronMeasMD5)
            cT.chronMeasMD5 = I.chronMeasMD5{i,2};
            end
        end
        C{i}.chronMeasurementTable{cmt}=cT;
        end
        
        
        %%%%%%END CHRON MEASUREMENT TABLE
        
        
        
        %%%%%%%START CHRON MODELS
        if isfield(I.chronData{i},'chronModel')
            for cm=1:length(I.chronData{i}.chronModel)
                CMS = I.chronData{i}.chronModel{cm};
                
                %%%%% CHRON MODEL TABLE
                if isfield(CMS,'summaryTable')
                    CMT=readLiPDTable(CMS.summaryTable,dirname);
                    CMT=processLiPDColumns(CMT);
                            if size(I.chronSummaryTableMD5,1)>=i        
                                CMT.summaryTableMD5=I.chronSummaryTableMD5{i,2};
                            end

                    C{i}.chronModel{cm}.summaryTable=cT;
                end
                
                %%%%% CHRON ENS TABLE
                if isfield(CMS,'ensembleTable')
                    CME=readLiPDTable(CMS.ensembleTable,dirname);
                    CME=processLiPDColumns(CME);
                            if size(I.chronEnsMD5,1)>=i        
                                CME.chronEnsembleMD5=I.chronEnsMD5{i,2};
                            end
                    C{i}.chronModel{cm}.ensembleTable=CME;
                    
                end
                
                %%%%% CALIBRATED AGE DATA
                if isfield(CMS,'distributionTable')
                    C{i}.chronModel{cm}.distributionTable=cell(1,1);
                    for ca = 1:length(CMS.distributionTable)
                        CASA=readLiPDTable(CMS.distributionTable{ca},dirname);
                        CASA=processLiPDColumns(CASA);
                        C{i}.chronModel{cm}.distributionTable(ca)={CASA};
                    end
                end
                
            end
        end
    end
else
C=NaN;

end