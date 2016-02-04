function deleteWorksheet(spreadsheetKey,worksheetKey,aToken)
%
import java.io.*;
import java.net.*;
import java.lang.*;
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings;

MAXITER=10;
success=false;

getURLStringList=['https://spreadsheets.google.com/feeds/worksheets/' spreadsheetKey '/private/full/' worksheetKey];
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
    
    xmlData=xmlread(con.getInputStream());
    con.disconnect(); clear con;

    % FIXME 5 is a magic number here...is there a way to do this more reliably?
    worksheetEditKey=xmlData.getElementsByTagName('entry').item(0).getElementsByTagName('link').item(5).getAttribute('href').toCharArray';
    worksheetEditKey(1:length([getURLStringList '/']))=[];
    
    getURLStringListNew=[getURLStringList '/' worksheetEditKey];
    
    con = urlreadwrite(mfilename,getURLStringListNew);
    con.setInstanceFollowRedirects(false);
    con.setRequestMethod( 'DELETE' );        
    con.setRequestProperty('Authorization',['Bearer ' aToken]);
        
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
    
