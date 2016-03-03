%first create a new spreadsheet
load('google_tokens.mat');

%see how long since last refresh; update if more than an hour
if ((now-lastUpdated)*24*60)>10
    
    % to refresh the Docs access token (usually expires after 1 hr) you'd call
    aTokenDocs=refreshAccessToken(client_id,client_secret,rTokenDocs);
    
    % to refresh the Spreadsheet access token (usually expires after 1 hr) you'd call
    aTokenSpreadsheet=refreshAccessToken(client_id,client_secret,rTokenSpreadsheet);
    
    %reset when last updated
    lastUpdated=now;
    save -append google_tokens.mat lastUpdated aTokenDocs aTokenSpreadsheet
end
