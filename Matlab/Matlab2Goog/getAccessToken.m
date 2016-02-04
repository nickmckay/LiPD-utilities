function [access_token,refresh_token,token_type]=getAccessToken(client_id, client_secret, scope)

deviceCodeString=urlread('https://accounts.google.com/o/oauth2/device/code','POST', {'client_id', client_id, 'scope', scope});

device_code=[];
user_code=[];
verification_url=[];

reply_commas=[1 strfind(deviceCodeString,',') length(deviceCodeString)];

for i=1:length(reply_commas)-1
    if ~isempty(strfind(deviceCodeString(reply_commas(i):reply_commas(i+1)),'device_code'))
        tmp=deviceCodeString(reply_commas(i):reply_commas(i+1));
        index_tmp_colon=strfind(tmp,':');
        tmp=tmp(index_tmp_colon+1:end); clear index_tmp_colon;
        index_quotes=find(tmp=='"');
        device_code=tmp(index_quotes(1)+1:index_quotes(2)-1); clear index_quotes tmp;
    end
    if ~isempty(strfind(deviceCodeString(reply_commas(i):reply_commas(i+1)),'user_code'))
        tmp=deviceCodeString(reply_commas(i):reply_commas(i+1));
        index_tmp_colon=strfind(tmp,':');
        tmp=tmp(index_tmp_colon+1:end); clear index_tmp_colon;
        index_quotes=find(tmp=='"');
        user_code=tmp(index_quotes(1)+1:index_quotes(2)-1); clear index_quotes tmp;
    end
    if ~isempty(strfind(deviceCodeString(reply_commas(i):reply_commas(i+1)),'verification_url'))
        tmp=deviceCodeString(reply_commas(i):reply_commas(i+1));
        index_tmp_colon=strfind(tmp,':');
        tmp=tmp(index_tmp_colon+1:end); clear index_tmp_colon;
        index_quotes=find(tmp=='"');
        verification_url=tmp(index_quotes(1)+1:index_quotes(2)-1); clear index_quotes tmp;
    end
end

display(['Open your browser and navigate to ' verification_url]);
display(['When prompted enter the user code ' user_code]);
input('Press any key when the above steps were successfully completed to continue ');

accessTokenString=urlread('https://accounts.google.com/o/oauth2/token','POST', ...
{'client_id', client_id, 'client_secret', client_secret, 'code', device_code, 'grant_type', 'http://oauth.net/grant_type/device/1.0'});

access_token=[];
refresh_token=[];
token_type=[];

reply_commas=[1 strfind(accessTokenString,',') length(accessTokenString)];

for i=1:length(reply_commas)-1
    if ~isempty(strfind(accessTokenString(reply_commas(i):reply_commas(i+1)),'access_token'))
        tmp=accessTokenString(reply_commas(i):reply_commas(i+1));
        index_tmp_colon=strfind(tmp,':');
        tmp=tmp(index_tmp_colon+1:end); clear index_tmp_colon;
        index_quotes=find(tmp=='"');
        access_token=tmp(index_quotes(1)+1:index_quotes(2)-1); clear index_quotes tmp;
    end
    if ~isempty(strfind(accessTokenString(reply_commas(i):reply_commas(i+1)),'token_type'))
        tmp=accessTokenString(reply_commas(i):reply_commas(i+1));
        index_tmp_colon=strfind(tmp,':');
        tmp=tmp(index_tmp_colon+1:end); clear index_tmp_colon;
        index_quotes=find(tmp=='"');
        token_type=tmp(index_quotes(1)+1:index_quotes(2)-1); clear index_quotes tmp;
    end
    if ~isempty(strfind(accessTokenString(reply_commas(i):reply_commas(i+1)),'refresh_token'))
        tmp=accessTokenString(reply_commas(i):reply_commas(i+1));
        index_tmp_colon=strfind(tmp,':');
        tmp=tmp(index_tmp_colon+1:end); clear index_tmp_colon;
        index_quotes=find(tmp=='"');
        refresh_token=tmp(index_quotes(1)+1:index_quotes(2)-1); clear index_quotes tmp;
    end
end


end
