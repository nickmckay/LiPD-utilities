function [cellValue]=getWorksheetRow(spreadSheetKey,workSheetKey,rowNumber,aToken)

import java.io.*;
import java.net.*;
import java.lang.*;
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings

cellValue='';
cellFormula='';
MAXITER=10;
success=false;

getURLStringList=['https://spreadsheets.google.com/feeds/cells/' spreadSheetKey '/' workSheetKey '/private/full?min-row=' num2str(rowNumber) '&max-row=' num2str(rowNumber)];
safeguard=0;

while (~success && safeguard<MAXITER)
    safeguard=safeguard+1;
    con = urlreadwrite(mfilename,getURLStringList);
    con.setInstanceFollowRedirects(false);
    con.setRequestMethod('GET');
    con.setDoInput(true);
    con.setRequestProperty('Content-Type','application/atom+xml;charset=UTF-8');
    con.setRequestProperty('Authorization',['Bearer ' aToken]);
    if (con.getResponseCode()~=200)
        con.disconnect();
        continue;
    end           
    success=true;
end
if success    
    cellValue=getRowFromXML(con)';
else
    display(['Last response was: ' num2str(con.getResponseCode) '/' con.getResponseMessage().toCharArray()']);
    clear con;
    return;
end
