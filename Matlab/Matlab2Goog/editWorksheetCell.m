function editWorksheetCell(spreadSheetKey,workSheetKey,rowNumber,columnNumber,cellValue,aToken)

import java.io.*;
import java.net.*;
import java.lang.*;
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings

MAXITER=20;
success=false;

getURLStringList=['https://spreadsheets.google.com/feeds/cells/' spreadSheetKey '/' workSheetKey '/private/full/R' num2str(rowNumber) 'C' num2str(columnNumber)];
safeguard=0;

while (~success && safeguard<MAXITER)
    safeguard=safeguard+1;
    con = urlreadwrite(mfilename,getURLStringList);
    con.setInstanceFollowRedirects(false);
    con.setRequestMethod( 'GET' );
    con.setDoInput( true );
    con.setRequestProperty('Content-Type','application/atom+xml;charset=UTF-8');
    con.setRequestProperty('Authorization',['Bearer ' aToken]);
    if (con.getResponseCode()~=200)
        con.disconnect();
        continue;
    end
    
    xmlData=xmlread(con.getInputStream());
    con.disconnect(); clear con;    
    editKey=xmlData.getElementsByTagName('entry').item(0).getElementsByTagName('link').item(1).getAttribute('href').toCharArray';
    editKey(1:length([getURLStringList '/']))=[];
    
    getURLStringListNew=[getURLStringList '/' editKey];
    con = urlreadwrite(mfilename,getURLStringListNew);
    con.setInstanceFollowRedirects(false);
    con.setRequestMethod('PUT');
    con.setDoOutput( true );
    con.setRequestProperty('Content-Type','application/atom+xml;charset=UTF-8');
    con.setRequestProperty('Authorization',['Bearer ' aToken]);
    event=['<entry xmlns=''http://www.w3.org/2005/Atom'' '...
        'xmlns:gs=''http://schemas.google.com/spreadsheets/2006''>' ...
        '<id>https://spreadsheets.google.com/feeds/cells/' spreadSheetKey '/' workSheetKey '/private/full/R' num2str(rowNumber) 'C' num2str(columnNumber) '</id>' ...
        '<link rel=''edit'' type=''application/atom+xml'' '...
        'href=''https://spreadsheets.google.com/feeds/cells/' spreadSheetKey '/' workSheetKey '/private/full/R' num2str(rowNumber) 'C' num2str(columnNumber) '/' editKey '''/>'...
        '<gs:cell row=''' num2str(rowNumber) ''' col=''' num2str(columnNumber) ''' inputValue="' cellValue '"/>'...
        '</entry>'];
    ps = PrintStream(con.getOutputStream());
    ps.print(event);
    ps.close(); clear ps;
    if (con.getResponseCode()~=200)
        con.disconnect();
        continue;
    end
    success=true;
end
if success
    con.disconnect(); clear con;
else
    display(['Last response was: ' num2str(con.getResponseCode) '/' con.getResponseMessage().toCharArray()']);
    clear con;
    return;
end
