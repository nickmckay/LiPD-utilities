%create bib table

%pubfields to include
pf={'citeKey','DOI','author','title','pubYear','journal','volume','issue','pages','citation','type'};

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

%restrict to good records
nPopulated = sum(~cellfun(@isempty,table2(:,2:(size(table2,2)-2))),2);
%exclude empties.
table2=table2(nPopulated>0,:);


%three
table3 = {gts.dataSetName}';

for j=1:length(pf)
    if isfield(gts,['pub3_' pf{j}])
        table3 = [table3 {gts.(['pub3_' pf{j}])}'];
    else
        table3 = [table3 repmat({''},size(table3,1),1)];
    end
end
for j=1:length(others)
    table3 = [table3 {gts.([others{j}])}'];
end
%append a 3
table3 = [table3 num2cell(2+ones(length(table3),1))];

%restrict to good records
nPopulated = sum(~cellfun(@isempty,table3(:,2:(size(table3,2)-2))),2);
%exclude empties.
table3=table3(nPopulated>0,:);



%four
table4 = {gts.dataSetName}';

for j=1:length(pf)
    if isfield(gts,['pub4_' pf{j}])
        table4 = [table4 {gts.(['pub4_' pf{j}])}'];
    else
        table4 = [table4 repmat({''},size(table4,1),1)];
        
    end
end
for j=1:length(others)
    table4 = [table4 {gts.([others{j}])}'];
end
%append a 4
table4 = [table4 num2cell(3+ones(length(table4),1))];


%restrict to good records
nPopulated = sum(~cellfun(@isempty,table4(:,2:(size(table4,2)-2))),2);
%exclude empties.
table4=table4(nPopulated>0,:);



%five
table5 = {gts.dataSetName}';

for j=1:length(pf)
    if isfield(gts,['pub5_' pf{j}])
        table5 = [table5 {gts.(['pub5_' pf{j}])}'];
    else
        table5 = [table5 repmat({''},size(table5,1),1)];
        
    end
end
for j=1:length(others)
    table5 = [table5 {gts.([others{j}])}'];
end
%append a 5
table5 = [table5 num2cell(4+ones(length(table5),1))];

%restrict to good records
nPopulated = sum(~cellfun(@isempty,table5(:,2:(size(table5,2)-2))),2);
%exclude empties.
table5=table5(nPopulated>0,:);









table = [table1 ; table2 ; table3 ; table4 ; table5];

%apply authorName conversion
table(:,4) = cellfun(@authorCell2BibtexAuthorString,table(:,4),'UniformOutput',0);

for i = 1:length(table)
    if ischar(table{i,2})
        table{i,2} = unicode2alpha(table{i,2});
    end
end



%deal with those with no keys
noKeys = find(cellfun(@isempty,table(:,2)));
noKeyTable = table(noKeys,:);

%get rid of duplicates
[uniqueKeys,uk1,uk2] = uniqueCell(table(:,2));
keyTable = table(uk1,:);

%remove instances of datasets that already have citeKeys
[a,b] = setdiff(noKeyTable(:,1),keyTable(:,1));
bigTable = [keyTable ; noKeyTable(b,:)];


cell2csv('~/Dropbox/pages2kphase2/bibData0708.txt',bigTable,'|');





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