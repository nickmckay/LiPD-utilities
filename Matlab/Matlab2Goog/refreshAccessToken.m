function access_token=refreshAccessToken(client_id, client_secret, refresh_token)

newAccessTokenString=urlread('https://accounts.google.com/o/oauth2/token','POST', ...
{'client_id', client_id, 'client_secret', client_secret, 'refresh_token', refresh_token, 'grant_type', 'refresh_token'});

access_token=[];

reply_commas=[1 strfind(newAccessTokenString,',') length(newAccessTokenString)];

for i=1:length(reply_commas)-1
    if ~isempty(strfind(newAccessTokenString(reply_commas(i):reply_commas(i+1)),'access_token'))
        tmp=newAccessTokenString(reply_commas(i):reply_commas(i+1));
        index_tmp_colon=strfind(tmp,':');
        tmp=tmp(index_tmp_colon+1:end); clear index_tmp_colon;
        index_quotes=find(tmp=='"');
        access_token=tmp(index_quotes(1)+1:index_quotes(2)-1); clear index_quotes tmp;
    end
end

end
