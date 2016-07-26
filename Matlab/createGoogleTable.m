function  T = createGoogleTable(T,L,pn,tn,dataName,tableName)

%create google table
checkGoogleTokens;


        
        
    %get the names of the columns
    colNames=structFieldNames(T);
    nCol=length(colNames);
    nRow=length(T.(colNames{1}).values)+2;
    %create a new spreadsheet, with two extra rows (for variable name
    %and TSID)
    display('creating new worksheet')   
    newWS=createWorksheet(L.googleSpreadSheetKey,nRow,nCol,[dataName num2str(pn) '-' tableName num2str(tn)],aTokenSpreadsheet);
    display(['created new worksheet ' newWS.worksheetKey])
    
    T.googleWorkSheetKey=newWS.worksheetKey;
    
    %go through the columns and populate the cells
    for c=1:nCol
        %check for TSid
        if ~isfield(T.(colNames{c}),'TSid')
            %create one - check against master list
            T.(colNames{c}).TSid=createTSID(T.(colNames{c}).variableName,L.dataSetName,L.googleSpreadSheetKey,T.googleWorkSheetKey);
        end
        
        if ~iscell(T.(colNames{c}).values)
            colData=[T.(colNames{c}).variableName; T.(colNames{c}).TSid; cellstr(num2str(T.(colNames{c}).values))];
        else
            colData=[T.(colNames{c}).variableName; T.(colNames{c}).TSid; T.(colNames{c}).values];
        end
        %figure out what column to put it in
        if isfield(T.(colNames{c}),'number')
            colNum=T.(colNames{c}).number;
        else
            colNum=c;
        end
        editWorksheetColumn(L.googleSpreadSheetKey,newWS.worksheetKey,colNum,1:nRow,colData,aTokenSpreadsheet);
    end
