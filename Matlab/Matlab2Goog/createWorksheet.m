function worksheetNew=createWorksheet(spreadsheetKey,rowCount,columnCount,worksheetTitle,aToken)
import java.io.*;
import java.net.*;
import java.lang.*;
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings;
worksheetNew=[];

getURLStringList=['https://spreadsheets.google.com/feeds/worksheets/' spreadsheetKey '/private/full'];

MAXITER=10;
success=false;
safeguard=0;

while (~success && safeguard<MAXITER)
    safeguard=safeguard+1;
    con = urlreadwrite(mfilename,getURLStringList);
    con.setInstanceFollowRedirects(false);
    con.setRequestMethod('POST');
    con.setDoOutput(true);
    con.setDoInput(true);
    con.setRequestProperty('Content-Type','application/atom+xml;charset=UTF-8');
    con.setRequestProperty('Authorization',['Bearer ' aToken]);
    event=['<entry xmlns=''http://www.w3.org/2005/Atom'''...
        ' xmlns:gs=''http://schemas.google.com/spreadsheets/2006''>'...
        '<category scheme=''http://schemas.google.com/spreadsheets/2006''' ...
        ' term=''http://schemas.google.com/spreadsheets/2006#worksheet''/>' ...
        '<title type=''text''>' worksheetTitle '</title>' ...
        '<content type=''text''>' worksheetTitle '</content>' ...
        '<gs:rowCount>' num2str(rowCount) '</gs:rowCount>' ...
        '<gs:colCount>' num2str(columnCount) '</gs:colCount>' ...
        '</entry>'];
    ps = PrintStream(con.getOutputStream());
    ps.print(event);
    ps.close();
    if (con.getResponseCode()~=201)
        con.disconnect();
        continue;
    end
    success=true;
end
if success
    xmlData=xmlread(con.getInputStream());
    con.disconnect(); clear con;
    worksheetNew.worksheetKey=xmlData.getElementsByTagName('id').item(0).getFirstChild.getData.toCharArray';
    worksheetNew.worksheetKey(1:length([getURLStringList '/']))=[];    
    worksheetNew.worksheetTitle=xmlData.getElementsByTagName('title').item(0).getFirstChild.getData.toCharArray';
    clear xmlData;    
else
    display(['Last response was: ' num2str(con.getResponseCode) '/' con.getResponseMessage().toCharArray()']);
    clear con;
    return;
end
