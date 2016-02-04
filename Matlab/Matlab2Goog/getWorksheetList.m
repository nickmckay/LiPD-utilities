function spreadsheetWorksheets=getWorksheetList(spreadsheetKey,aToken)

import java.io.*;
import java.net.*;
import java.lang.*;
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings;

spreadsheetWorksheets=[];

MAXITER=10;
success=false;

getURLStringList=['https://spreadsheets.google.com/feeds/worksheets/' spreadsheetKey '/private/full'];
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
    for genericIndex=0:xmlData.getElementsByTagName('entry').getLength-1
        spreadsheetWorksheets(genericIndex+1).worksheetKey=xmlData.getElementsByTagName('entry').item(genericIndex).getElementsByTagName('id').item(0).getFirstChild.getData.toCharArray';
        spreadsheetWorksheets(genericIndex+1).worksheetKey(1:length([getURLStringList '/']))=[];
        spreadsheetWorksheets(genericIndex+1).worksheetTitle=xmlData.getElementsByTagName('entry').item(genericIndex).getElementsByTagName('title').item(0).getFirstChild.getData.toCharArray';
    end
    clear xmlData;
else
    display(['Last response was: ' num2str(con.getResponseCode) '/' con.getResponseMessage().toCharArray()']);
    clear con;
    return;
end
