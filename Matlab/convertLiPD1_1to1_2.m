function L=convertLiPD1_1to1_2(L,forceConvert)


if nargin<2
    forceConvert = 0;
end

if ~isfield(L,'LiPDVersion')
    
    L.LiPDVersion = 1.0;
end

if ischar(L.LiPDVersion)
    L.LiPDVersion = str2num(L.LiPDVersion);
end

if L.LiPDVersion == 1.1 | forceConvert
    %handle chronData first
    if isfield(L,'chronData')
        
        for i = 1:length(L.chronData);
            C=L.chronData{i};
            if isfield(C,'chronMeasurementTable')
                if ~iscell(C.chronMeasurementTable)
                    %convert measurement table to set
                    newCM{1}=C.chronMeasurementTable;
                    C.chronMeasurementTable=newCM;
                end
            end
            
            if isfield(C,'chronModel')
                for j=1:length(C.chronModel)
                    CM=C.chronModel{j};
                    if isfield(CM,'chronModelTable')
                        CM.summaryTable=CM.chronModelTable;
                    end
                    if isfield(CM,'calibratedAges')
                        CM.distributionTable=CM.calibratedAges;
                    end
                    CM=rmfieldsoft(CM,{'chronModelTable','calibratedAges'});
                    C.chronModel{j} = CM;
                end
            end
            
            L.chronData{i}=C;
        end
        
    end
    
    %now PaleoData changes.
    if isfield(L,'paleoData')
        pnames=fieldnames(L.paleoData);
        for i = 1:length(pnames)
            %for now force it.
            if 1 % ~isfield(L.paleoData.(pnames{i}),'number') |  ~isfield(L.paleoData.(pnames{i}),'paleoMeasurementTableNumber') %assume each paleodatatable is a different record
                newP{i}.paleoMeasurementTable{1}=L.paleoData.(pnames{i});
                
            else
                newP{L.paleoData.(pnames{i}).number}.paleoMeasurementTable{L.paleoData.(pnames{i}).paleoMeasurementTableNumber}=L.paleoData.(pnames{i});
                newP{L.paleoData.(pnames{i}).number}.paleoMeasurementTable{L.paleoData.(pnames{i}).paleoMeasurementTableNumber}=rmfieldsoft(newP{L.paleoData.(pnames{i}).number}.paleoMeasurementTable{L.paleoData.(pnames{i}).paleoMeasurementTableNumber},{'paleoRecordNumber','paleoMeasurementTableNumber','number'});
                
            end
        end
        
        
        L.paleoData=newP;
    end
    
    L.LiPDVersion = 1.2;
    
end

