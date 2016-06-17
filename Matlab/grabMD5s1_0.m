if bagged

%get tag manifest MD5
tmd5=table2cell(readtable('../tagmanifest-md5.txt','readVariableNames',0,'delimiter',' '));
tmd5=tmd5{3,1};

%read in MD5 sums for individual files
md5=table2cell(readtable('../manifest-md5.txt','readVariableNames',0,'delimiter',' '));

metaRow=find(~cellfun(@isempty,strfind(md5(:,3),'.json')));
paleoRow=find(~cellfun(@isempty,strfind(md5(:,3),'PaleoData.csv')));
chronRow=find(~cellfun(@isempty,strfind(md5(:,3),'Chron')));


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

chronMD5=cell(length(chronRow),2);
%assign appropriately
for i=1:length(chronRow)
    tose=md5{chronRow(i),3};
    endPiece=strfind(tose,'.Chron');
    priorPeriod=max(strfind(tose(1:(endPiece-1)),'.'));
    chronMD5{i,1}=tose(priorPeriod+1:endPiece-1);
    chronMD5{i,2}=md5{chronRow(i),1};
end

%assign in MD5's
I.paleoMD5=paleoMD5;
I.chronMD5=chronMD5;
I.tagMD5=tmd5;
I.metadataMD5=metaMD5;
else
 %assign in MD5's
I.paleoMD5=NaN;
I.chronMD5=NaN;
I.tagMD5=NaN;
I.metadataMD5=NaN;
end
