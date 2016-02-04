clear variables; clc;
%

if (exist('google_tokens.mat', 'file')==0)
    % you can obtain the client_id and client_secret from Google developer console for an app
    % that uses Drive API (select Other for Application type)

    % get new tokens
    client_id='713034401403-7j6meq80a7vs9sf6dc3m1aa8q3idfgpt.apps.googleusercontent.com'; 
    client_secret='c-H9tfPQiDYDmoLfBCqVemgL';

    if (isempty(client_id)||isempty(client_secret))
        display('Must get your own client id and client secret from Google developer console');
        return;
    end

    % allow this application to access drive API
    display('Getting Google Drive API token');
    scope_docs='https://docs.google.com/feeds';
    [aTokenDocs,rTokenDocs,tokenTypeDocs]=getAccessToken(client_id,client_secret,scope_docs);


    % allow this application to access spreadsheet API
    display('Getting Google Spreadsheet API token');
    scope_spreadsheet='https://spreadsheets.google.com/feeds';
    [aTokenSpreadsheet,rTokenSpreadsheet,tokenTypeSpreadsheet]=getAccessToken(client_id,client_secret,scope_spreadsheet);

    save('google_tokens.mat');
else
    load('google_tokens.mat');
    % to refresh the Docs access token (usually expires after 1 hr) you'd call
    aTokenDocs=refreshAccessToken(client_id,client_secret,rTokenDocs);

    % to refresh the Spreadsheet access token (usually expires after 1 hr) you'd call
    aTokenSpreadsheet=refreshAccessToken(client_id,client_secret,rTokenSpreadsheet);
end

if isempty(aTokenDocs) || isempty(aTokenSpreadsheet)
    warndlg('Could not obtain authorization tokens from Google.','');
    return;
end
%%
% creating a new spreadsheet requires a file upload
% you can create the new spreadsheet from an empty file or from a file of your choice
% here we use the empty file provided : default.ods
% make sure to set the appropriate mime time
% xls is application/vnd.ms-excel
% xlsx is application/vnd.openxmlformats-officedocument.spreadsheetml.sheet 
% ods is application/vnd.oasis.opendocument.spreadsheet
spreadSheetNew=createSpreadsheet('testMatlabNew',aTokenDocs,'default.ods','application/vnd.oasis.opendocument.spreadsheet');

% to test spreadsheet deletion enable the following two lines
%deleteSpreadsheet(spreadSheetNew.spreadsheetKey,aTokenDocs);
%return

% default conversion from ods will generate a worksheet with name testMatlabNew
% add another worksheet called Sheet
rowCount=10;
colCount=7;
worksheetTitleNew='Sheet';
worksheetNew=createWorksheet(spreadSheetNew.spreadsheetKey,rowCount,colCount,worksheetTitleNew,aTokenSpreadsheet);

% get the list of worksheets, should have testMatlabNew and Sheet
spreadsheetWorksheets=getWorksheetList(spreadSheetNew.spreadsheetKey,aTokenSpreadsheet);

% rename and resize the Sheet worksheet created above to SheetDefault and size 1x1
selectWorksheet='Sheet';
selectWorksheetIndex=strmatch(selectWorksheet,{spreadsheetWorksheets.worksheetTitle},'exact');
if ~isempty(selectWorksheetIndex)
    rowCountNew=1;
    colCountNew=1;
    worksheetTitleNew='SheetDefault';
    changeWorksheetNameAndSize(spreadSheetNew.spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,rowCountNew,colCountNew,worksheetTitleNew,aTokenSpreadsheet);    
%     to test worksheet deletion within a spreadsheet enable the following two lines; this will also be tested below
%     deleteWorksheet(spreadSheetNew.spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,aTokenSpreadsheet);
%     return
end

% we should now have two worksheets in spreadsheet testMatlabNew: testMatlabNew and SheetDefault
% get a list of spreadsheets using Sheets API
userSpreadsheets=getSpreadsheetList(aTokenSpreadsheet);

% select testMatlabNew spreadsheet
selectSpreadsheet='testMatlabNew';
selectSpreadsheetIndex=strmatch(selectSpreadsheet,{userSpreadsheets.spreadsheetTitle},'exact');
if ~isempty(selectSpreadsheetIndex)
    % select worksheet SheetDefault in spreadsheet testMatlabNew and change its name to Sheet1 and size to 3x5
    % we will delete this worksheet named Sheet1 later
    spreadsheetWorksheets=getWorksheetList(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,aTokenSpreadsheet);
    
    selectWorksheet='SheetDefault';
    selectWorksheetIndex=strmatch(selectWorksheet,{spreadsheetWorksheets.worksheetTitle},'exact');
    if ~isempty(selectWorksheetIndex)
        rowCountNew=3;
        colCountNew=5;
        worksheetTitleNew='Sheet1';
        changeWorksheetNameAndSize(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,rowCountNew,colCountNew,worksheetTitleNew,aTokenSpreadsheet);
    end
    spreadsheetWorksheets=getWorksheetList(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,aTokenSpreadsheet);
    
    % single cell based editing
    % create a new worksheet named Sheet size 3x4
    rowCount=3;
    colCount=4;
    worksheetTitleNew='Sheet';
    spreadsheetWorksheets(length(spreadsheetWorksheets)+1)=createWorksheet(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,rowCount,colCount,worksheetTitleNew,aTokenSpreadsheet);
    spreadsheetWorksheets=getWorksheetList(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,aTokenSpreadsheet);

    % write some values and formulas in Sheet worksheet
    selectWorksheet='Sheet';
    selectWorksheetIndex=strmatch(selectWorksheet,{spreadsheetWorksheets.worksheetTitle},'exact');
    if ~isempty(selectWorksheetIndex)
        for rowIndex=1:rowCount
            for colIndex=1:colCount
                if colIndex<colCount || colCount==1
                    editWorksheetCell(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,rowIndex,colIndex,num2str(rand),aTokenSpreadsheet);
                else
                    % square the value in the previous column by entering
                    % formula.
                    editWorksheetCell(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,rowIndex,colIndex,'=R[0]C[-1]*R[0]C[-1]',aTokenSpreadsheet);
                end
            end
        end
    end
    
    % read values from worksheet Sheet
    for rowIndex=1:rowCount
        for colIndex=1:colCount
            [tempVar1,tempVar2]=getWorksheetCell(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,rowIndex,colIndex,aTokenSpreadsheet);
            worksheetValues(rowIndex,colIndex)={tempVar1};
            worksheetFormulas(rowIndex,colIndex)={tempVar2};
            clear tempVar1 tempVar2;
        end
    end

    % multicell based editing with batch requests
    % create a new worksheet named Sheet2 size 5x8
    rowCount=5;
    colCount=8;
    worksheetTitleNew='Sheet2';
    spreadsheetWorksheets(length(spreadsheetWorksheets)+1)=createWorksheet(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,rowCount,colCount,worksheetTitleNew,aTokenSpreadsheet);
    spreadsheetWorksheets=getWorksheetList(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,aTokenSpreadsheet);

    % write some values and formulas in Sheet2 worksheet
    selectWorksheet='Sheet2';
    selectWorksheetIndex=strmatch(selectWorksheet,{spreadsheetWorksheets.worksheetTitle},'exact');
    % write some random values in columns 1, 3 and 4; we'll later square the values in column 1 in column 2 and add values in cols 3 4 in column 5
    for rowIndex=1:rowCount
        editWorksheetRow(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,rowIndex,[1 3 4],{num2str(rand) num2str(rand) num2str(rand)},aTokenSpreadsheet);
    end
    % write square formula in column 2, sum columns 3 and 4 in column 5
    for rowIndex=1:rowCount
        editWorksheetRow(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,rowIndex,[2 5],{'=R[0]C[-1]*R[0]C[-1]' '=R[0]C[-2]+R[0]C[-1]'},aTokenSpreadsheet);
    end
    % read values from worksheet Sheet2
    for rowIndex=1:rowCount
        for colIndex=1:colCount
            [tempVar1,tempVar2]=getWorksheetCell(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,rowIndex,colIndex,aTokenSpreadsheet);
            worksheetValues(rowIndex,colIndex)={tempVar1};
            worksheetFormulas(rowIndex,colIndex)={tempVar2};
            clear tempVar1 tempVar2;
        end
    end

    % multicell based editing with batch requests
    % create a new worksheet named Sheet2 size 5x8
    rowCount=5;
    colCount=8;
    worksheetTitleNew='Sheet3';
    spreadsheetWorksheets(length(spreadsheetWorksheets)+1)=createWorksheet(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,rowCount,colCount,worksheetTitleNew,aTokenSpreadsheet);
    spreadsheetWorksheets=getWorksheetList(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,aTokenSpreadsheet);

    % write some values and formulas in Sheet3 worksheet
    selectWorksheet='Sheet3';
    selectWorksheetIndex=strmatch(selectWorksheet,{spreadsheetWorksheets.worksheetTitle},'exact');
    % write some random values in rows 1, 3 and 4; we'll later square the values in row 1 in row 2 and add values in rows 3 4 in row 5
    for colIndex=1:colCount
        editWorksheetColumn(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,colIndex,[1 3 4],{num2str(rand) num2str(rand) num2str(rand)},aTokenSpreadsheet);
    end
    % write square formula in row 2, sum rows 3 and 4 in row 5
    for colIndex=1:colCount
        editWorksheetColumn(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,colIndex,[2 5],{'=R[-1]C[0]*R[-1]C[0]' '=R[-2]C[0]+R[-1]C[0]'},aTokenSpreadsheet);
    end
    % read values from worksheet Sheet3
    for rowIndex=1:rowCount
        for colIndex=1:colCount
            [tempVar1,tempVar2]=getWorksheetCell(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,rowIndex,colIndex,aTokenSpreadsheet);
            worksheetValues(rowIndex,colIndex)={tempVar1};
            worksheetFormulas(rowIndex,colIndex)={tempVar2};
            clear tempVar1 tempVar2;
        end
    end

    % get the list of worksheets again
    spreadsheetWorksheets=getWorksheetList(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,aTokenSpreadsheet);

    % delete worksheet Sheet1
    selectWorksheet='Sheet1';
    selectWorksheetIndex=strmatch(selectWorksheet,{spreadsheetWorksheets.worksheetTitle});
    if ~isempty(selectWorksheetIndex)
         deleteWorksheet(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,spreadsheetWorksheets(selectWorksheetIndex).worksheetKey,aTokenSpreadsheet);
    end
    % show updated list of worksheets in spreadsheet testMatlabNew
    spreadsheetWorksheets=getWorksheetList(userSpreadsheets(selectSpreadsheetIndex).spreadsheetKey,aTokenSpreadsheet);
end
