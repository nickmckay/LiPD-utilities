function I = readLiPDGeo1_0(I)

%%%%BEGIN GEO SECTION %%%%%%%%%%%%%%%

if isfield(I.geo,'geometry')
    
    %load in geo information
    if numel(I.geo.geometry.coordinates)<2
        I.geo.latitude=NaN;
        I.geo.meanLat=NaN;
        I.geo.longitude=NaN;
        I.geo.meanLon=NaN;
    else
        I.geo.latitude=I.geo.geometry.coordinates(:,2);
        I.geo.meanLat=nanmean(I.geo.latitude);
        I.geo.longitude=I.geo.geometry.coordinates(:,1);
        I.geo.meanLon=nanmean(I.geo.longitude);
    end
    
    %if theres elevation/depth, grab it too
    if size(I.geo.geometry.coordinates,2)>2
        I.geo.elevation= I.geo.geometry.coordinates(:,3);
        I.geo.meanElev=mean(I.geo.elevation);
    end
    I.geo=rmfield(I.geo,'geometry');

else
    I.geo.latitude=NaN;
    I.geo.meanLat=NaN;
    I.geo.longitude=NaN;
    I.geo.meanLon=NaN;
    
end

%bring property fields up a level
if isfield(I.geo,'properties')
 if isstruct(I.geo.properties)
    propFields=fieldnames(I.geo.properties);
    for pf=1:length(propFields)
        I.geo.(propFields{pf})=I.geo.properties.(propFields{pf});
    end
 end
%remove properties and coordiantes structures
I.geo=rmfield(I.geo,'properties');
end
%%%%%%%END GEO SECTION %%%%%%%%%