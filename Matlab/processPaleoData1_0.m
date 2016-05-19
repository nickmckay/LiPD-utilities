function P = processPaleoData1_0(I)
P=I;

%paleodata
for i=length(I.paleoData)
    for j=1:length(I.paleoData{i}.columns)
        %quick fix rename parameter to variableName
        if isfield(I.paleoData{i}.columns{j},'parameter') & ~isfield(I.paleoData{i}.columns{j},'variableName')
            I.paleoData{i}.columns{j}.variableName=I.paleoData{i}.columns{j}.parameter;
            I.paleoData{i}.columns{j}=rmfield(I.paleoData{i}.columns{j},'parameter');
        end
        newname=genvarname(I.paleoData{i}.columns{j}.variableName,fieldnames(P.paleoData{i}));
        P.paleoData{i}.(newname)=I.paleoData{i}.columns{j};
    end
    NS.(genvarname(P.paleoData{i}.paleoDataTableName))=P.paleoData{i};
    NS.(genvarname(P.paleoData{i}.paleoDataTableName))=rmfield(NS.(genvarname(P.paleoData{i}.paleoDataTableName)),'columns');
    
    %add in MD5. PaleoData MD5
    whichMD5=find(strcmp(P.paleoData{i}.paleoDataTableName,I.paleoMD5(:,1)));
    if isempty(whichMD5) & size(paleoMD5,1)==1
        whichMD5=1;
    end
    if ~isempty(whichMD5)
        NS.(genvarname(P.paleoData{i}.paleoDataTableName)).paleoDataMD5=I.paleoMD5{whichMD5,2};
    end
end
P.paleoData=NS;
P=rmfield(P,'paleoMD5');

