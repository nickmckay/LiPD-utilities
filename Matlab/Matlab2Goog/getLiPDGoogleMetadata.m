function GTS=getLiPDGoogleMetadata(skey,wkey)
checkGoogleTokens;
%get base metadata

metadata=getWorksheet(skey,wkey,aTokenSpreadsheet);

%how many TS entries?
%where does it start?
pds=find(strcmp(metadata(:,1),'paleoData column metadata'));

%where does it end?
pde=size(metadata,1);

nTS=pde-(pds+1);
%%

clear toFindc
%find key names
toFind={'Bas','Pub','Geo'};
%where does it start?

for i=1:length(toFind)
    
    toFindc(i)=find(strncmpi(toFind{i},metadata(1,:),3));
    
    
end
%%
%pull metadata from pub, base and geo
for c=toFindc
    r=2;
    
    while 1
        value=metadata{r,c};
        if isempty(value)
            break
        end
        for ts=1:nTS
            GTS(ts).(value)=convertCellStringToNumeric(metadata(r,c+1));
        end
        r=r+1;
    end
end

%%
%pull metadata from paleoData
for c=1:size(metadata,2)
    value=metadata{pds+1,c};
    if isempty(value)
        break
    end
    toPop=metadata((pds+2):end,c);
    [GTS.(value)]=toPop{:};
end

