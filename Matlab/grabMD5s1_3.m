%only works if its bagged
if bagged
    
    %get tag manifest MD5
    tmd5=table2cell(readtable('../tagmanifest-md5.txt','readVariableNames',0,'delimiter',' '));
    tmd5=tmd5{3,1};
    
    %read in MD5 sums for individual files
    md5=table2cell(readtable('../manifest-md5.txt','readVariableNames',0,'delimiter',' '));
    
    metaRow=find(~cellfun(@isempty,strfind(md5(:,end),'.json')));
    paleoMeasurementRow=find(~cellfun(@isempty,strfind(md5(:,end),'measurement')) & ~cellfun(@isempty,strfind(md5(:,end),'paleo')));
    chronMeasurementRow=find(~cellfun(@isempty,strfind(md5(:,end),'measurement')) & ~cellfun(@isempty,strfind(md5(:,end),'Chron')));
    chronEnsembleRow=find(~cellfun(@isempty,strfind(md5(:,end),'Ensemble')) & ~cellfun(@isempty,strfind(md5(:,end),'Chron')));
    chronSummaryRow=find(~cellfun(@isempty,strfind(md5(:,end),'summaryTable')) & ~cellfun(@isempty,strfind(md5(:,end),'Chron')));
    paleoEnsembleRow=find(~cellfun(@isempty,strfind(md5(:,end),'Ensemble')) & ~cellfun(@isempty,strfind(md5(:,end),'paleo')));
    paleoSummaryRow=find(~cellfun(@isempty,strfind(md5(:,end),'summaryTable')) & ~cellfun(@isempty,strfind(md5(:,end),'paleo')));
    
    metaMD5=md5{metaRow,1};
    
    paleoMeasMD5=cell(length(paleoMeasurementRow),2);
    %assign appropriately
    for i=1:length(paleoMeasurementRow)
        tose=md5{paleoMeasurementRow(i),end};
        endPiece=strfind(tose,'.measurementTable');
        priorPeriod=max(strfind(tose(1:(endPiece-1)),'.'));
        paleoMeasMD5{i,1}=tose(priorPeriod+1:endPiece-1);
        paleoMeasMD5{i,2}=md5{paleoMeasurementRow(i),1};
    end
    
    chronMeasMD5=cell(length(chronMeasurementRow),2);
    %assign appropriately
    for i=1:length(chronMeasurementRow)
        tose=md5{chronMeasurementRow(i),end};
        endPiece=strfind(tose,'.measurementTable');
        priorPeriod=max(strfind(tose(1:(endPiece-1)),'.'));
        chronMeasMD5{i,1}=tose(priorPeriod+1:endPiece-1);
        chronMeasMD5{i,2}=md5{chronMeasurementRow(i),1};
    end
    
    chronEnsMD5=cell(length(chronEnsembleRow),2);
    %assign appropriately
    for i=1:length(chronEnsembleRow)
        tose=md5{chronEnsembleRow(i),end};
        endPiece=strfind(tose,'.EnsembleTable');
        priorPeriod=max(strfind(tose(1:(endPiece-1)),'.'));
        chronEnsMD5{i,1}=tose(priorPeriod+1:endPiece-1);
        chronEnsMD5{i,2}=md5{chronEnsembleRow(i),1};
    end
    
    chronSummaryMD5=cell(length(chronSummaryRow),2);
    %assign appropriately
    for i=1:length(chronSummaryRow)
        tose=md5{chronSummaryRow(i),end};
        endPiece=strfind(tose,'.summaryTable');
        priorPeriod=max(strfind(tose(1:(endPiece-1)),'.'));
        chronSummaryMD5{i,1}=tose(priorPeriod+1:endPiece-1);
        chronSummaryMD5{i,2}=md5{chronSummaryRow(i),1};
    end
    
    paleoEnsMD5=cell(length(paleoEnsembleRow),2);
    %assign appropriately
    for i=1:length(paleoEnsembleRow)
        tose=md5{paleoEnsembleRow(i),end};
        endPiece=strfind(tose,'.EnsembleTable');
        priorPeriod=max(strfind(tose(1:(endPiece-1)),'.'));
        paleoEnsMD5{i,1}=tose(priorPeriod+1:endPiece-1);
        paleoEnsMD5{i,2}=md5{paleoEnsembleRow(i),1};
    end
    
    paleoSummaryMD5=cell(length(paleoSummaryRow),2);
    %assign appropriately
    for i=1:length(paleoSummaryRow)
        tose=md5{paleoSummaryRow(i),end};
        endPiece=strfind(tose,'.summaryTable.csv');
        priorPeriod=max(strfind(tose(1:(endPiece-1)),'.'));
        paleoSummaryMD5{i,1}=tose(priorPeriod+1:endPiece-1);
        paleoSummaryMD5{i,2}=md5{paleoSummaryRow(i),1};
    end
    
    %assign in MD5's
    I.paleoMeasMD5=paleoMeasMD5;
    I.chronMeasMD5=chronMeasMD5;
    I.chronEnsMD5=chronEnsMD5;
    I.chronSummaryTableMD5=chronSummaryMD5;
    I.paleoEnsMD5=paleoEnsMD5;
    I.paleoSummaryTableMD5=paleoSummaryMD5;
    I.tagMD5=tmd5;
I.metadataMD5=metaMD5;
else
    %assign in MD5's
    I.paleoMeasMD5=NaN;
    I.chronMeasMD5=NaN;
    I.chronEnsMD5=NaN;
    I.chronSummaryTableMD5=NaN;
    I.paleoEnsMD5=NaN;
    I.paleoSummaryTableMD5=NaN;
    I.tagMD5=NaN;
I.metadataMD5=NaN;
    
end





