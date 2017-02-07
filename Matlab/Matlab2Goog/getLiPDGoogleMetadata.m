function [GTS,GTSC]=getLiPDGoogleMetadata(skey,wkey)
checkGoogleTokens;
%get base metadata
metadata=getWorksheet(skey,wkey,aTokenSpreadsheet);
%remove all of the blank rows!
br=zeros(size(metadata,1),1);
for r=1:size(metadata,1)
if all(cellfun(@isempty,metadata(r,:)));
    br(r)=1;
end
end
isbr = find(br);
if ~isempty(isbr)
    metadata=metadata(setdiff(1:size(metadata,1),isbr),:);
end

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
    pde=cds-1;
    cde=size(metadata,1);
    nTSC=cde-(cds+1);
end

nTS=pde-(pds+1);

%%

clear toFindc
%find key names
toFind={'Bas','Pub','Geo','Fun'};
%where does it start?

toFindc(1) = find(strncmpi(toFind{1},metadata(1,:),3));
for i=2:length(toFind)
    if ~isempty(find(strncmpi(toFind{i},metadata(1,:),3)))
    
    toFindc=[toFindc find(strncmpi(toFind{i},metadata(1,:),3))];
    end
    
end
%%
%pull metadata from pub, base and geo
for c=toFindc
    r=2;
    
    while 1
        value=metadata{r,c};
        if isempty(value) | strncmpi(value,'paleodata ',10)
            break
        end
        for ts=1:nTS
            if isempty(strfind(value,'_DOI'))
            GTS(ts).(value)=convertCellStringToNumeric(metadata(r,c+1));
            else
                GTS(ts).(value)=metadata{r,c+1};

            end
        end
        r=r+1;
    end
    
    if isChron
        r=2;
        
        while 1
            value=metadata{r,c};
        if isempty(value) | strncmpi(value,'paleodata ',10)
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

GTS = renameTS(GTS,0,1,0);

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
    GTSC = renameTS(GTSC,0,1,0);
end


