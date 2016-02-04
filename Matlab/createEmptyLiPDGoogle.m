function L=createEmptyLiPDGoogle(dataSetName)
%creates a blank LiPD google file
E=readLiPD('Empty.lpd');

%create a new TSid

tsidCell=GetGoogleSpreadsheet('15IsdiTf790BRPXVL7GsW_j7wrQDHIEB9NmFI0lqqMuY');

%generate new random TSID
stringHex = '01234567879abcdef';
while 1
    TSid = ['LPD' stringHex(ceil(rand(1, 8)*length(stringHex)))];
    %make sure it doesn't exist
    if ~any(strcmp(TSid,tsidCell(:,1)))
        break
    end
end
E.paleoData.data.EXAMPLE.TSid=TSid;%for first one

%repeat for year
while 1
    TSid = ['LPD' stringHex(ceil(rand(1, 8)*length(stringHex)))];
    %make sure it doesn't exist
    if ~any(strcmp(TSid,tsidCell(:,1)))
        break
    end
end
E.paleoData.data.year.TSid=TSid;%for second one

%assign in the  name
E.dataSetName=dataSetName;

%write it to google
L=createLiPDGoogleFile(E,1);
end