if bagged

%get tag manifest MD5
tmd5=table2cell(readtable('../tagmanifest-md5.txt','readVariableNames',0,'delimiter',' '));
tmd5=tmd5{3,1};

%read in MD5 sums for individual files
md5=table2cell(readtable('../manifest-md5.txt','readVariableNames',0,'delimiter',' '));

metaRow=find(~cellfun(@isempty,strfind(md5(:,3),'.json')));
paleoRow=find(~cellfun(@isempty,strfind(md5(:,3),'PaleoData.csv')));
chronMeasurementRow=find(~cellfun(@isempty,strfind(md5(:,3),'ChronMeasurement')));
chronEnsembleRow=find(~cellfun(@isempty,strfind(md5(:,3),'Ensemble')));
chronModelTableRow=find(~cellfun(@isempty,strfind(md5(:,3),'ChronModelTable')));


metaMD5=md5{metaRow,1};

paleoMD5=cell(length(paleoRow),2);
%assign appropriately
for i=1:length(paleoRow)
    tose=md5{paleoRow(i),3};
    endPiece=strfind(tose,'.PaleoData.csv');
    priorPeriod=max(strfind(tose(1:(endPiece-1)),'.'));
    paleoMD5{i,1}=tose(priorPeriod+1:endPiece-1);
    paleoMD5{i,2}=md5{paleoRow(i),1};
end

chronMeasMD5=cell(length(chronMeasurementRow),2);
%assign appropriately
for i=1:length(chronMeasurementRow)
    tose=md5{chronMeasurementRow(i),3};
    endPiece=strfind(tose,'.ChronMeasurementTable.csv');
    priorPeriod=max(strfind(tose(1:(endPiece-1)),'.'));
    chronMeasMD5{i,1}=tose(priorPeriod+1:endPiece-1);
    chronMeasMD5{i,2}=md5{chronMeasurementRow(i),1};
end

chronEnsMD5=cell(length(chronEnsembleRow),2);
%assign appropriately
for i=1:length(chronEnsembleRow)
    tose=md5{chronEnsembleRow(i),3};
    endPiece=strfind(tose,'.EnsembleTable.csv');
    priorPeriod=max(strfind(tose(1:(endPiece-1)),'.'));
    chronEnsMD5{i,1}=tose(priorPeriod+1:endPiece-1);
    chronEnsMD5{i,2}=md5{chronEnsembleRow(i),1};
end

chronMTMD5=cell(length(chronEnsembleRow),2);
%assign appropriately
for i=1:length(chronEnsembleRow)
    tose=md5{chronEnsembleRow(i),3};
    endPiece=strfind(tose,'.ChronModelTable.csv');
    priorPeriod=max(strfind(tose(1:(endPiece-1)),'.'));
    chronMTMD5{i,1}=tose(priorPeriod+1:endPiece-1);
    chronMTMD5{i,2}=md5{chronEnsembleRow(i),1};
end

%assign in MD5's
I.paleoMD5=paleoMD5;
I.chronMeasMD5=chronMeasMD5;
I.chronEnsMD5=chronEnsMD5;
I.chronModelTableMD5=chronMTMD5;
I.tagMD5=tmd5;
I.metadataMD5=metaMD5;


else%assign in MD5's
I.paleoMD5=NaN;
I.chronMeasMD5=NaN;
I.chronEnsMD5=NaN;
I.chronModelTableMD5=NaN;
I.tagMD5=NaN;
I.metadataMD5=NaN;
end
