function [CTS,L] = flattenChronMeasurementTable(L)

%if no verions, force to 1.0
if ~isfield(L,'LiPDVersion')
    L.LiPDVersion = 1.0;
end

if L.LiPDVersion == 1.0
    display('updating LiPD file to current version')
    L = convertLiPD1_0to1_1(L);
end

LC=L;
LC = rmfield(LC,'paleoData');
for i = 1:length(L.chronData)
    if ~isfield(L.chronData{i},'chronName')
        L.chronData{i}.chronName  = ['chron' num2str(i)];
    end
    if isfield(L.chronData{i},'chronMeasurementTable')
        for j=1:length(L.chronData{i}.chronMeasurementTable)
            %make sure there's an age column
%             colNames = structFieldNames(L.chronData{i}.chronMeasurementTable{j});
%             if all(~strcmp('age',colNames))
%                 display('There are no columns named "age" - this is required.')
%                 toShow = strcat(stringifyCells(num2cell(1:length(colNames))'),repmat({' - '},length(colNames),1),colNames);
%                 display(toShow)
%                 whichIsAge=input('Which column is the age column (this will overwrite the name to age); press 0 if none are');
%                 if ~ismember(whichIsAge,1:length(colNames))
%                     error('Your chronMeasurementTable must have an age column')
%                 end
%                 L.chronData{i}.chronMeasurementTable{j}.(colNames{whichIsAge}).variableName = 'age';
%                 if isfield(L.chronData{i}.chronMeasurementTable{j}.(colNames{whichIsAge}),'notes')
%                     L.chronData{i}.chronMeasurementTable{j}.(colNames{whichIsAge}).notes = [ L.chronData{i}.chronMeasurementTable{j}.(colNames{whichIsAge}).notes ; 'renamed from ' colNames{whichIsAge}];
%                     
%                 else
%                     L.chronData{i}.chronMeasurementTable{j}.(colNames{whichIsAge}).notes = ['renamed from ' colNames{whichIsAge}];
%                     
%                 end
%                 L.chronData{i}.chronMeasurementTable{j}.age =L.chronData{i}.chronMeasurementTable{j}.(colNames{whichIsAge});
%                 L.chronData{i}.chronMeasurementTable{j}=rmfield(L.chronData{i}.chronMeasurementTable{j},colNames{whichIsAge});
%             end
            
            LC.paleoData{i}.paleoMeasurementTable{j}=L.chronData{i}.chronMeasurementTable{j};
        end
        LC.paleoData{i}.paleoMeasurementTable{j}.paleoName=L.chronData{i}.chronName;
    end
end

hasChron = 0;
LC=rmfield(LC,'chronData');



try 
    CTS=extractTimeseries(LC,1);
    hasChron=1;
catch me
    warning('chron extraction failed, skipping')
end


if hasChron
    f=fieldnames(CTS);
    pid=f(find(~cellfun(@isempty,(strfind(f,'identifier')))&strncmpi('pub',f,3)));
    if ~isempty(pid)%remove any pub identifiers, if there are any
        CTS=rmfield(CTS,pid);
    end
    
    %chronData name
    %[CTS.chronData_chronName] = CTS.paleoData_paleoDataTableName;
    [CTS.chronData_chronNumber] = CTS.paleoData_paleoNumber;
    [CTS.chronData_chronMeasurementTableNumber] = CTS.paleoData_paleoMeasurementTableNumber;
    
    CTS = rmfieldsoft(CTS,{'paleoData_paleoDataTableName','paleoData_paleoMeasurementTableNumber','paleoData_paleoNumber'});
    cfnames =fieldnames(CTS);
    pdi=(find(strncmpi('paleoData_',cfnames,10)));
    for cp = 1:length(pdi)
        curname=cfnames{pdi(cp)};
        newname=['chron' curname(6:end)];
        [CTS.(newname)]=CTS.(curname);
        CTS=rmfield(CTS,curname);
    end
    
else
    CTS=NaN;
    
end





