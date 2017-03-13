function TSid=createTSID(variableName,dataSetName,spreadsheetKey,worksheetKey,altName,tsidPath,checkWeb)
%generates and registers a new TSID name. checkWeb boolean forces the code
%to get the list from the master file each time, slow if running many times
%in one session. Leaving checkWeb empty allows for smart choosing of when
%to download (once an hour)
%altName proposes a TSid, rather than generating randomly
load LiPDUtilitiesPreferences
if nargin<6
   tsidPath=githubPath;
end
   
if nargin<7
    checkWeb=0;
    
    curdir=pwd;
    
    %for nick - edit if you want to keep this in a certain spot on your
    %computer
    cd(tsidPath)
    
    
    d=dir('tsidCell.mat');
    if length(d)>0
        load tsidCell.mat lastSync
        howLong=(now-lastSync)*24*60;
        if howLong<60
            checkWeb=0;
        end
    end
end

if checkWeb
    tsidCell=GetGoogleSpreadsheet('15IsdiTf790BRPXVL7GsW_j7wrQDHIEB9NmFI0lqqMuY');
    tsidCell=tsidCell(2:end,:);
else
    load tsidCell.mat tsidCell
end

if nargin>4
    TSid=altName;
    if any(strcmp(TSid,tsidCell(:,1)))
        error('proposed name already exists')
    end
else
    
    while 1
        %generate new random TSID
        stringHex = '01234567879abcdef';
        TSid = ['LPD' stringHex(ceil(rand(1, 8)*length(stringHex)))];
        %make sure it doesn't exist
        if ~any(strcmp(TSid,tsidCell(:,1)))
            break
        end
    end
end
%add to list
tsidCell=[tsidCell; {TSid} {dataSetName} {variableName} {spreadsheetKey} {worksheetKey}];


checkGoogleTokens;
%save to google
editWorksheetRow('15IsdiTf790BRPXVL7GsW_j7wrQDHIEB9NmFI0lqqMuY','od6',size(tsidCell,1)+1,1:size(tsidCell,2),tsidCell(end,:),aTokenSpreadsheet);
lastSync=now;


%creat local copy
save tsidCell.mat tsidCell lastSync
cd(curdir);

