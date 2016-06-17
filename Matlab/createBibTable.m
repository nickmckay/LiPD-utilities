%create bib table

%pubfields to include
pf={'citeKey','DOI','author','title','pubYear','journal','volume','issue','pages','citation'};

%also inlude dataSetName and originalDataset
others = {'originalDataURL'};

good = find(strcmp({TS.paleoData_useInGlobalTemperatureAnalysis}','TRUE') & strcmp({TS.climateInterpretation_variable}','T'));

gts=TS(good);
table1 = {gts.dataSetName}';
for j=1:length(pf)
    table1 = [table1 {gts.(['pub1_' pf{j}])}'];
end
for j=1:length(others)
    table1 = [table1 {gts.([others{j}])}'];
end

%append a 1
table1 = [table1 num2cell(ones(length(table1),1))];

table2 = {gts.dataSetName}';
for j=1:length(pf)
    table2 = [table2 {gts.(['pub2_' pf{j}])}'];
end
for j=1:length(others)
    table2 = [table2 {gts.([others{j}])}'];
end
%append a 2
table2 = [table2 num2cell(1+ones(length(table2),1))];

table = [table1 ; table2];

%apply authorName conversion
table(:,4) = cellfun(@authorCell2BibtexAuthorString,table(:,4),'UniformOutput',0);

for i = 1:length(table)
    if ischar(table{i,2})
table{i,2} = unicode2alpha(table{i,2});
    end
end


%restrict to good records
nPopulated = sum(~cellfun(@isempty,table(:,2:size(table,2))),2);
%exclude empties. 
table=table(nPopulated>0,:);

%deal with those with no keys
noKeys = find(cellfun(@isempty,table(:,2)));
noKeyTable = table(noKeys,:);

%get rid of duplicates
[uniqueKeys,uk1,uk2] = uniqueCell(table(:,2));
keyTable = table(uk1,:);

%remove instances of datasets that already have citeKeys
[a,b] = setdiff(noKeyTable(:,1),keyTable(:,1));
bigTable = [keyTable ; noKeyTable(b,:)];


cell2csv('~/Dropbox/pages2kphase2/bibData0617.txt',bigTable,'|');





% 
% table = [row1 ; row2];
% for i =2:length(gts)
%     
%     row1 = gts(i).dataSetName;
%     for j=1:length(pf)
%         row1 = [row1 gts(i).(['pub1_' pf{j}])];
%     end
%     for j=1:length(others)
%         row1 = [row1 gts(i).([others{j}])];
%     end
%     
%     
%     
%     %2nd row
%     row2 = gts(i).dataSetName;
%     for j=1:length(pf)
%         row2 = [row2 gts(i).(['pub1_' pf{j}])];
%     end
%     for j=1:length(others)
%         row2 = [row2 gts(i).([others{j}])];
%     end
%     
%     table = [table ; row1 ; row2];
%     
%     
% end