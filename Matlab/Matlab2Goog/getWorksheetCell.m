function [cellValue,cellFormula]=getWorksheetCell(spreadSheetKey,workSheetKey,rowNumber,columnNumber,aToken)

import java.io.*;
import java.net.*;
import java.lang.*;
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings

cellValue='';
cellFormula='';
MAXITER=10;
success=false;

getURLStringList=['https://spreadsheets.google.com/feeds/cells/' spreadSheetKey '/' workSheetKey '/private/full/R' num2str(rowNumber) 'C' num2str(columnNumber)];
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
    xmlData=xmlread(con.getInputStream());
    con.disconnect(); clear con;
    cellValue=xmlData.getElementsByTagName('entry').item(0).getElementsByTagName('content').item(0).getTextContent.toCharArray';
    cellFormula=xmlData.getElementsByTagName('entry').item(0).getElementsByTagName('gs:cell').item(0).getAttribute('inputValue').toCharArray';
    clear xmlData;
else
    display(['Last response was: ' num2str(con.getResponseCode) '/' con.getResponseMessage().toCharArray()']);
    clear con;
    return;
end
