function C=readLiPDPaleoData1_3(I,dirname)


toct=NaN;
if isfield(I,'paleoData')
    C=I.paleoData;
    toct=1:length(I.paleoData);
end



if ~isnan(toct) %if there are paleo tables, load em in
    for i = toct; %go through each paleoology
        if isfield(I.paleoData{i},'measurementTable')
            %%%%%paleo MEASUREMENT TABLE
            %Go through measurementTable first
            for pmt=1:length(I.paleoData{i}.measurementTable)
                cT = I.paleoData{i}.measurementTable{pmt};
                
                cT=readLiPDTable(cT,dirname);
                cT=processLiPDColumns(cT);
                if size(I.paleoMeasMD5,1)>=i
                    if iscell(I.paleoMeasMD5)
                        cT.measurementTableMD5 = I.paleoMeasMD5{i,2};
                    end
                end
                C{i}.measurementTable{pmt}=cT;
            end
        end
        %%%%%%END paleo MEASUREMENT TABLE
        
        
        
        %%%%%%%START paleo MODELS
        if isfield(I.paleoData{i},'model')
            for cm=1:length(I.paleoData{i}.model)
                CMS = I.paleoData{i}.model{cm};
                
                %%%%% paleo SUMMARY TABLE
                if isfield(CMS,'summaryTable')
                    for ccc = 1:length(CMS.summaryTable)
                        CMT=readLiPDTable(CMS.summaryTable{ccc},dirname);
                        CMT=processLiPDColumns(CMT);
%                         if size(I.paleoSummaryTableMD5,1)>=i
%                             CMT.summaryTableMD5=I.paleoSummaryTableMD5{i,2};
%                         end
                        
                        C{i}.model{cm}.summaryTable{ccc}=CMT;
                    end
                end
                
                %%%%% paleo ENS TABLE
                if isfield(CMS,'ensembleTable')
                    for ccc = 1:length(CMS.ensembleTable)
                        CME=readLiPDTable(CMS.ensembleTable{ccc},dirname);
                        CME=processLiPDColumns(CME);
%                         if size(I.paleoEnsTableMD5,1)>=i
%                             CME.paleoEnsembleMD5=I.paleoEnsMD5{i,2};
%                         end
                        C{i}.model{cm}.ensembleTable{ccc}=CME;
                    end
                    
                end
                
                %%%%% CALIBRATED AGE DATA
                if isfield(CMS,'distributionTable')
                    C{i}.model{cm}.distributionTable=cell(1,1);
                    for ca = 1:length(CMS.distributionTable)
                        CASA=readLiPDTable(CMS.distributionTable{ca},dirname);
                        CASA=processLiPDColumns(CASA);
                        C{i}.model{cm}.distributionTable(ca)={CASA};
                    end
                end
                
            end
        end
    end
else
    C=NaN;
    
end