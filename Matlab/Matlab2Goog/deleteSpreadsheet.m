function deleteSpreadsheet(spreadsheetKey,aToken)
%
import java.io.*;
import java.net.*;
import java.lang.*;
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings;

MAXITER=10;
success=false;

getURLStringList=['https://www.googleapis.com/drive/v2/files/' spreadsheetKey ];
safeguard=0;
while (~success && safeguard<MAXITER)        
    safeguard=safeguard+1;
    con = urlreadwrite(mfilename,getURLStringList);
    con.setRequestMethod('DELETE');
    con.setRequestProperty('Authorization',['Bearer ' aToken]);        
    % first reply is with code 204, second will issue 404
    if (con.getResponseCode()~=404)    
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
    
