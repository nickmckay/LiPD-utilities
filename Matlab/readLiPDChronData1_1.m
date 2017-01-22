function C=readLiPDChronData1_1(I,dirname)


toct=NaN;
if isfield(I,'chronData')
    C=I.chronData;
    toct=1:length(I.chronData);
end



if ~isnan(toct) %if there are chron tables, load em in
    for i = toct; %go through each chronology
        %%%%%CHRON MEASUREMENT TABLE
        %Go through chronMeasurementTable first
        cT = I.chronData{i}.chronMeasurementTable;
        
        cT=readLiPDTable(cT,dirname);
        cT=processLiPDColumns(cT);
        if iscell(I.chronMeasMD5)
        cT.chronMeasurementTableMD5 = I.chronMeasMD5{i,2};
        end
        C{i}.chronMeasurementTable=cT;
        
        %%%%%%END CHRON MEASUREMENT TABLE
        
        
        
        %%%%%%%START CHRON MODELS
        if isfield(I.chronData{i},'chronModel')
            for cm=1:length(I.chronData{i}.chronModel)
                CMS = I.chronData{i}.chronModel{cm};
                
                %%%%% CHRON MODEL TABLE
                if isfield(CMS,'chronModelTable')
                    CMT=readLiPDTable(CMS.chronModelTable,dirname);
                    CMT=processLiPDColumns(CMT);
                    CMT.chronModelTableMD5=I.chronModelTableMD5{i,2};

                    C{i}.chronModel{cm}.chronModelTable=cT;
                end
                
                %%%%% CHRON ENS TABLE
                if isfield(CMS,'ensembleTable')
                    CME=readLiPDTable(CMS.ensembleTable,dirname);
                    CME=processLiPDColumns(CME);
                    CME.chronEnsembleMD5=I.chronEnsMD5{i,2};
                    C{i}.chronModel{cm}.ensembleTable=CME;
                    
                end
                
                %%%%% CALIBRATED AGE DATA
                if isfield(CMS,'calibratedAges')
                    C{i}.chronModel{cm}.calibratedAges=cell(1,1);
                    for ca = 1:length(CMS.calibratedAges)
                        CASA=readLiPDTable(CMS.calibratedAges{ca},dirname);
                        CASA=processLiPDColumns(CASA);
                        C{i}.chronModel{cm}.calibratedAges(ca)={CASA};
                    end
                end
                
            end
        end
    end
else
C=NaN;

end