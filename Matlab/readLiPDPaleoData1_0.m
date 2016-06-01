function P=readLiPDPaleoData1_0(I,dirname)

if ~isfield(I,'paleoData')
   error('LiPD file does not include paleoData section; this is required')
end

tomt=1:length(I.paleoData);

%load in paleoDataTables
for i =tomt;
    I.paleoData{i}=processLiPDColumns(readLiPDTable(I.paleoData{i},dirname));
    if i==1
        P.(makeValidName(I.paleoData{i}.paleoDataTableName))=I.paleoData{i};
    else
        P.(makeUniqueStrings(I.paleoData{i}.paleoDataTableName,fieldnames(P)))=I.paleoData{i};
    end
end


