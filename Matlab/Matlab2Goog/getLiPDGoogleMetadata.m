function [GTS,GTSC]=getLiPDGoogleMetadata(skey,wkey)
checkGoogleTokens;
%get base metadata

metadata=getWorksheet(skey,wkey,aTokenSpreadsheet);

%how many paleodataTS entries?
%where does it start?
pds=find(strcmp(metadata(:,1),'paleoData column metadata'));

%is there chrondata?
cds=find(strcmp(metadata(:,1),'chronData column metadata'));

if isempty(cds)
    isChron=0;
    pde=size(metadata,1);
    GTSC=NaN;
else
    isChron=1;
    pde=cds-2;
    cde=size(metadata,1);
    nTSC=cde-(cds+1);
end

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
    
    if isChron
        r=2;
        
        while 1
            value=metadata{r,c};
            if isempty(value)
                break
            end
            for ts=1:nTSC
                GTSC(ts).(value)=convertCellStringToNumeric(metadata(r,c+1));
            end
            r=r+1;
        end
    end
end

%%
%pull metadata from paleoData
for c=1:size(metadata,2)
    value=metadata{pds+1,c};
    if ~isempty(value)
        
        toPop=metadata((pds+2):pde,c);
        [GTS.(value)]=toPop{:};
    end
end

%%
%pull metadata from chronData
if isChron
    for c=1:size(metadata,2)
        value=metadata{cds+1,c};
        if ~isempty(value)
            
            toPop=metadata((cds+2):cde,c);
            [GTSC.(value)]=toPop{:};
        end
    end
end

