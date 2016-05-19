function P = processChronData1_0(P,I)

toct=NaN;
if isfield(I,'chronData')
    toct=1:length(I.chronData);
end
%chron
if ~isnan(toct)
    for i=toct
        for j=1:length(I.chronData{i}.columns)
            newname=genvarname(I.chronData{i}.columns{j}.variableName,fieldnames(P.chronData{i}));
            P.chronData{i}.(newname)=I.chronData{i}.columns{j};
        end
        NS.(genvarname(P.chronData{i}.chronDataTableName))=P.chronData{i};
        NS.(genvarname(P.chronData{i}.chronDataTableName))=rmfield(NS.(genvarname(P.chronData{i}.chronDataTableName)),'columns');
        %add in MD5. ChronData MD5
        whichMD5c=find(strcmp(P.chronData{i}.chronDataTableName,chronMD5(:,1)));
        if isempty(whichMD5c) & size(chronMD5,1)==1
            whichMD5c=1;
        end
        if ~isempty(whichMD5c)
            NS.(genvarname(P.chronData{i}.chronDataTableName)).chronDataMD5=chronMD5{whichMD5c,2};
        end
    end
    P.chronData=NS;
end