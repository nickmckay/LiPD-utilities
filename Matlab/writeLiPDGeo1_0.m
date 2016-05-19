function LiPDStruct = writeLiPDGeo(LiPDStruct)

%%%%%BEGIN GEO SECTION %%%%%%%%%%
%check for latitude and longitude
if isfield(LiPDStruct.geo,'meanLat') & ~isfield(LiPDStruct.geo,'latitude')
    LiPDStruct.geo.latitude=LiPDStruct.geo.meanLat;
end
if isfield(LiPDStruct.geo,'meanLon') & ~isfield(LiPDStruct.geo,'longitude')
    LiPDStruct.geo.longitude=LiPDStruct.geo.meanLon;
end

%deal with strings
if isfield(LiPDStruct.geo,'latitude')
    if ischar(LiPDStruct.geo.latitude)
        LiPDStruct.geo.latitude=str2num(LiPDStruct.geo.latitude);
    end
end
if isfield(LiPDStruct.geo,'longitude')
    if ischar(LiPDStruct.geo.longitude)
        LiPDStruct.geo.longitude=str2num(LiPDStruct.geo.longitude);
    end
end
if isfield(LiPDStruct.geo,'elevation')
    if ischar(LiPDStruct.geo.elevation)
        LiPDStruct.geo.elevation=str2num(LiPDStruct.geo.elevation);
    end
end

%write coordinates back into geometry
if isfield(LiPDStruct.geo,'elevation')
    if isstruct(LiPDStruct.geo.elevation)
        if length(LiPDStruct.geo.elevation.value)~=length(LiPDStruct.geo.latitude)
            LiPDStruct.geo.geometry.coordinates=[LiPDStruct.geo.latitude LiPDStruct.geo.longitude repmat(LiPDStruct.geo.elevation.value,length(LiPDStruct.geo.latitude),1)];
        else
            LiPDStruct.geo.geometry.coordinates=[LiPDStruct.geo.latitude LiPDStruct.geo.longitude LiPDStruct.geo.elevation.value];
        end
        
    else
        if length(LiPDStruct.geo.elevation)~=length(LiPDStruct.geo.latitude)
            LiPDStruct.geo.geometry.coordinates=[LiPDStruct.geo.latitude LiPDStruct.geo.longitude repmat(LiPDStruct.geo.elevation,length(LiPDStruct.geo.latitude),1)];
        else
            LiPDStruct.geo.geometry.coordinates=[LiPDStruct.geo.latitude LiPDStruct.geo.longitude LiPDStruct.geo.elevation];
        end
    end
else
    LiPDStruct.geo.geometry.coordinates=[LiPDStruct.geo.latitude LiPDStruct.geo.longitude];
end

%write string properties into properties
gs=fieldnames(LiPDStruct.geo);
for s=1:length(gs)
    if ischar(LiPDStruct.geo.(gs{s})) & ~strcmp(gs{s},'type')
        LiPDStruct.geo.properties.(gs{s})=LiPDStruct.geo.(gs{s});
    end
end

%all geo objects should be features
LiPDStruct.geo.type='Feature';

%clean up fields that shouldn't be there
goodGeo={'type','geometry','properties'};
for s=1:length(gs)
    if ~strcmp(gs{s},goodGeo)
        LiPDStruct.geo=rmfield(LiPDStruct.geo,gs{s});
    end
end

%%%%%END GEO SECTION %%%%%%%%%%