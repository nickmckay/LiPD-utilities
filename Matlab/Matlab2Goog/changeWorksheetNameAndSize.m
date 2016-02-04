function changeWorksheetNameAndSize(spreadsheetKey,worksheetKey,rowCountNew,colCountNew,worksheetTitleNew,aToken)
%
import java.io.*;
import java.net.*;
import java.lang.*;
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings;

getURLStringList=['https://spreadsheets.google.com/feeds/worksheets/' spreadsheetKey '/private/full/' worksheetKey];

MAXITER=10;
success=false;
safeguard=0;

while (~success && safeguard<MAXITER)
    safeguard=safeguard+1;
    % get the edit key of the worksheet
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
    
    % edit the worksheet using PUT request
    con = urlreadwrite(mfilename,getURLStringListNew);
    con.setInstanceFollowRedirects(false);
    con.setRequestMethod('PUT');
    con.setDoOutput(true);
    con.setDoInput(true);
    con.setRequestProperty('Content-Type','application/atom+xml;charset=UTF-8');
    con.setRequestProperty('Authorization',['Bearer ' aToken]);
    event=['<entry xmlns=''http://www.w3.org/2005/Atom'''...
        ' xmlns:gs=''http://schemas.google.com/spreadsheets/2006''>' ...
        '<id>https://spreadsheets.google.com/feeds/worksheets/' spreadsheetKey '/private/full/' worksheetKey '</id>' ...
        '<category scheme=''http://schemas.google.com/spreadsheets/2006''' ...
        ' term=''http://schemas.google.com/spreadsheets/2006#worksheet''/>' ...
        '<title type=''text''>' worksheetTitleNew '</title>' ...
        '<content type=''text''>' worksheetTitleNew '</content>' ...
        '<link rel=''http://schemas.google.com/spreadsheets/2006#listfeed''' ...
        ' type=''application/atom+xml'' href=''https://spreadsheets.google.com/feeds/list/' spreadsheetKey '/' worksheetKey '/private/full''/>'...
        '<link rel=''http://schemas.google.com/spreadsheets/2006#cellsfeed''' ...
        ' type=''application/atom+xml'' href=''https://spreadsheets.google.com/feeds/cells/' spreadsheetKey '/' worksheetKey '/private/full''/>' ...
        '<link rel=''self'' type=''application/atom+xml'' href=''https://spreadsheets.google.com/feeds/worksheets/' spreadsheetKey '/private/full/' worksheetKey '''/>' ...
        '<link rel=''edit'' type=''application/atom+xml'''...
        ' href=''https://spreadsheets.google.com/feeds/worksheets/' spreadsheetKey '/private/full/' worksheetKey '/'  worksheetEditKey '''/>'...
        '<gs:rowCount>' num2str(rowCountNew) '</gs:rowCount><gs:colCount>' num2str(colCountNew) '</gs:colCount>'...
        '</entry>'];
    ps = PrintStream(con.getOutputStream());
    ps.print(event);
    ps.close();
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
