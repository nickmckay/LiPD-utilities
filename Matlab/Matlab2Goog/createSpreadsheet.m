function spreadsheetNew=createSpreadsheet(spreadsheetTitle,aToken,upload_file_name,upload_mime_type)
%
import java.io.*;
import java.net.*;
import java.lang.*;
import com.mathworks.mlwidgets.io.InterruptibleStreamCopier;
com.mathworks.mlwidgets.html.HTMLPrefs.setProxySettings;
spreadsheetNew=[];

getURLStringList='https://www.googleapis.com/upload/drive/v2/files?uploadType=resumable&convert=true';

MAXITER=10;
success=false;
safeguard=0;

% metadata POST request
while (~success && safeguard<MAXITER)
    safeguard=safeguard+1;
    con = urlreadwrite(mfilename,getURLStringList);
    con.setInstanceFollowRedirects(false);
    con.setRequestMethod('POST');
    con.setDoOutput(true);
    con.setDoInput(true);

    con.setRequestProperty('Authorization',['Bearer ' aToken]);
    con.setRequestProperty('Content-Type','application/json; charset=UTF-8');        
    con.setRequestProperty('X-Upload-Content-Type', upload_mime_type);        
    con.setRequestProperty('X-Upload-Content-Length', '0');

    event=['{"title":"' spreadsheetTitle '"}'];
    con.setRequestProperty('Content-Length', num2str(length(event)));

    ps = PrintStream(con.getOutputStream());
    ps.print(event);
    ps.close();  clear ps event;  
    if (con.getResponseCode()~=200)
        con.disconnect();
        continue;
    end
    success=true;
end
put_url=[];
if (~success)
    display(['Last response (POST) was: ' num2str(con.getResponseCode) '/' con.getResponseMessage().toCharArray()']);
    return;
else
    con.disconnect();
    headerIndex = 0;
    while (~isempty(char(con.getHeaderField(headerIndex))))
        if (strcmpi(char(con.getHeaderFieldKey(headerIndex)),'location'))
            put_url=char(con.getHeaderField(headerIndex));
            break;
        end
        headerIndex = headerIndex+1;
    end
end
if (isempty(put_url))
    display(['Could not get PUT url from POST response.']);
    return;
end

fid=fopen(upload_file_name,'r');
if (fid==-1)
    display(['Could not open file ' upload_file_name ' for reading']);
    return;
end
file_data=int8(fread(fid,Inf));
spreadsheetNew.fileData=file_data;
fclose(fid); clear fid;

success=false;
safeguard=0;

while (~success && safeguard<MAXITER)
    safeguard=safeguard+1;
    con=urlreadwrite(mfilename,put_url);
    con.setInstanceFollowRedirects(false);
    con.setRequestMethod('PUT');
    con.setDoOutput(true);
    con.setDoInput(true);
    con.setRequestProperty('Content-Type', upload_mime_type);        
    con.setRequestProperty('Content-Length', num2str(length(file_data)));
    ps = PrintStream(con.getOutputStream());
    ps.print(file_data);
    ps.close();  clear ps file_data;
    if (con.getResponseCode()~=200)
        con.disconnect();
        continue; 
    end
    success=true;
end
if (~success)
    display(['Last response (PUT) was: ' num2str(con.getResponseCode) '/' con.getResponseMessage().toCharArray()']);
    return;
else
    inputStream = con.getInputStream;
    byteArrayOutputStream = java.io.ByteArrayOutputStream;
    isc = InterruptibleStreamCopier.getInterruptibleStreamCopier;
    isc.copyStream(inputStream,byteArrayOutputStream);
    inputStream.close;
    byteArrayOutputStream.close; 
    con.disconnect();
    spreadsheet_info=char(byteArrayOutputStream.toByteArray)';
    tok_self_link=strfind(spreadsheet_info, 'selfLink');
    if (isempty(tok_self_link))
        return;
    end
    tok_self_link=tok_self_link(1)-1; % include the "
    tok_end_self_link=strfind(spreadsheet_info(tok_self_link:end),',');
    tok_end_self_link=tok_end_self_link(1)+tok_self_link-2;
    spreadsheet_self_link=spreadsheet_info(tok_self_link:tok_end_self_link);
    tok_title=strfind(spreadsheet_info, 'title');
    if (isempty(tok_title))
        return;
    end
    tok_title=tok_title(1)-1; % include the "
    tok_end_title=strfind(spreadsheet_info(tok_title:end),',');
    tok_end_title=tok_end_title(1)+tok_title-2;
    spreadsheet_title=spreadsheet_info(tok_title:tok_end_title);
    spreadsheet_self_link=spreadsheet_self_link(strfind(spreadsheet_self_link,':')+1:end);
    spreadsheet_self_link_quotes=strfind(spreadsheet_self_link,'"');
    spreadsheet_self_link=spreadsheet_self_link(spreadsheet_self_link_quotes(1)+1:spreadsheet_self_link_quotes(2)-1);
    spreadsheet_self_link_slash=strfind(spreadsheet_self_link,'/');
    spreadsheet_self_link_slash=spreadsheet_self_link_slash(end);
    spreadsheet_self_link=spreadsheet_self_link(spreadsheet_self_link_slash+1:end);
    spreadsheet_title=spreadsheet_title(strfind(spreadsheet_title,':')+1:end);
    spreadsheet_title_quotes=strfind(spreadsheet_title,'"');
    spreadsheet_title=spreadsheet_title(spreadsheet_title_quotes(1)+1:spreadsheet_title_quotes(2)-1);
    spreadsheetNew.spreadsheetKey=spreadsheet_self_link;
    spreadsheetNew.spreadsheetTitle=spreadsheet_title;
end

end
