function [cellValue]=getWorksheetColumn(spreadSheetKey,workSheetKey,columnNumber,aToken,warnings)
import java.io.*;
import java.net.*;
import java.lang.*;
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings
if nargin<5
    warnings=1;
end
cellValue='';
cellFormula='';
MAXITER=10;
success=false;

getURLStringList=['https://spreadsheets.google.com/feeds/cells/' spreadSheetKey '/' workSheetKey '/private/full?min-col=' num2str(columnNumber) '&max-col=' num2str(columnNumber)];
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
    cellValue=getColumnFromXML(con);
else
    if warnings
    display(['Last response was: ' num2str(con.getResponseCode) '/' con.getResponseMessage().toCharArray()']);
    end
    clear con;
    return;
end
