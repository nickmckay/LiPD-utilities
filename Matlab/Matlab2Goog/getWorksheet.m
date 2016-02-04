function [ss]=getWorksheet(spreadSheetKey,workSheetKey,aToken)
% spreadSheetKey=L.googleSpreadSheetKey;
% workSheetKey= L.googleMetadataWorksheet;
% aToken=aTokenSpreadsheet;


c=1;

while 1
    col=getWorksheetColumn(spreadSheetKey,workSheetKey,c,aToken,0);
    if c>1
        if length(col)==0
            break
        end
        
        %deal with the fact that it won't grab blank columns at the bottom
        %of the spreadsheet
        ml=max([ml, length(col)]);
        while length(col)<ml
            col=[col ;{''}];
        end
 
        while size(ss,1)<ml %add rows to ss until it's the length of ml
            ss=[ss ; repmat({' '},1,size(ss,2))];
        end
        ss=cat(2,ss,col);

        
    else
        ss=col;
        ml=length(col);
    end
    c=c+1;
end

