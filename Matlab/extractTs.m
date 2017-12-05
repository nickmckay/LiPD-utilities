function TS = extractTs(D,whichTables,mode)


if nargin <= 2
    mode = 'paleo';
end

if nargin == 1
    whichTables = 'all';
end

breakFlag=0;
dsn = structFieldNames(D);
h = waitbar(0,'Extracting your timeseries...');

for d = 1:length(dsn)
    waitbar(d/length(dsn),h);
%    display(dsn{d})
    if breakFlag
        break
    end
    % Is this a single dataset? We'll know if the dataSetName is = the root.
    if isfield(D,'dataSetName')
        L=D;
        breakFlag=1;
    else
        % Dataset library? That's our only other assumption if the first 'if' doesn't work.
        L = D.(dsn{d}); %grab just one LiPD file
    end
    
    % dataSetName not provided. Exit(1), we can't continue without it.
    if ~isfield(L,'dataSetName')
        error([dsn{d} ' has no dataSetName. This is forbidden.'])
    end
    
    if strcmp(mode,'chron')
        %artificially switch chron and paleodata (hackers gonna hack)
        newL = L;
        newL.paleoData = L.chronData;
        newL.chronData = L.paleoData;
        L = newL;
    end
    
    
    % dataSetName not provided. Exit(1), we can't continue without it.
    if ~isfield(L,'paleoData')
        switch mode
            case 'paleo'
                error([dsn{d} ' has no paleoData. This is forbidden.'])
            case 'chron'
                %maybe this isn't what I want - skip if it's missing?
                error([dsn{d} ' has no chronData. You cant extract in chronMode if theres no chronData.'])
        end
    end
    
    
    
    %Loop through paleoData objects
    for p = 1:length(L.paleoData)
        %Loop through paleoMeasurementTables
        if strcmp(whichTables,'all') ||  strncmpi(whichTables,'meas',4)
            
            for pm = 1:length(L.paleoData{p}.measurementTable)
                PM = L.paleoData{p}.measurementTable{pm};%grab this measurmentTable
                
                %grab all the data for this row
                miniTS = populateTsRow(PM,L,'measurementTable',p,NaN,pm);
                
                %append to currentTS
                if ~exist('TS')
                    TS = miniTS;
                else
                    TS = appendStruct(TS,miniTS);
                end
                
                
            end %loop through paleo measurement tables
        end
        
        
        %get ensemble and/or summary table
        if strcmp(whichTables,'all') |  strncmpi(whichTables,'summ',4) |  strncmpi(whichTables,'ens',3)
            %now loop through paleomodels
            if isfield(L.paleoData{p},'model')
                for pmod = 1:length(L.paleoData{p}.model) %loop through paleomodels
                    
                    if isfield(L.paleoData{p}.model{pmod},'summaryTable') & (strncmpi(whichTables,'summ',4) | strcmp(whichTables,'all')) %if summary table
                        for sss = 1:length(L.paleoData{p}.model{pmod}.summaryTable)
                            %grab all the data for this row
                            PM = L.paleoData{p}.model{pmod}.summaryTable{sss};%grab this summaryTable
                            miniTS = populateTsRow(PM,L,'summaryTable',p,pmod,sss);
                            
                            %append to currentTS
                            if ~exist('TS')
                                TS = miniTS;
                            else
                                TS = appendStruct(TS,miniTS);
                            end
                        end%loop through summary table
                    end%if summary table
                    
                    
                    if isfield(L.paleoData{p}.model{pmod},'ensembleTable') & (strncmpi(whichTables,'ens',3) | strcmp(whichTables,'all')) %if ensemble table
                        for sss = 1:length(L.paleoData{p}.model{pmod}.ensembleTable)
                            %grab all the data for this row
                            PM = L.paleoData{p}.model{pmod}.ensembleTable{sss};%grab this ensembleTable
                            miniTS = populateTsRow(PM,L,'ensembleTable',p,pmod,sss);
                            
                            %append to currentTS
                            if ~exist('TS')
                                TS = miniTS;
                            else
                                TS = appendStruct(TS,miniTS);
                            end
                            
                            
                        end%loop through ensemble table
                    end%if ensemble table
                    
                    
                    
                end%loop through paleomodels
            end%if there are paleomodels
        end
        
        
    end %loop through paleoData objects
    
    
    
    
    
end

%calculate temporal resolution metadata...
if isfield(TS,'year')
    if ~any(cellfun(@iscell,{TS.year}))
        dat = cellfun(@(x) nanmedian(abs(diff(x))), {TS.year},'UniformOutput',0);
        [TS.hasResolution_hasMedianValue] = dat{:};
        dat = cellfun(@(x) nanmean(abs(diff(x))), {TS.year},'UniformOutput',0);
        [TS.hasResolution_hasMeanValue] = dat{:};
        dat = cellfun(@(x) nanmax(abs(diff(x))), {TS.year},'UniformOutput',0);
        [TS.hasResolution_hasMaxValue] = dat{:};
        dat = cellfun(@(x) nanmin(abs(diff(x))), {TS.year},'UniformOutput',0);
        [TS.hasResolution_hasMinValue] = dat{:};
        [TS.hasResolution_units] = TS.yearUnits;
    else
        warning('Some of your year columns are cells, so I cant calculate resolution')
    end
elseif isfield(TS,'age')
    if ~any(cellfun(@iscell,{TS.age}))
        
        dat = cellfun(@(x) nanmedian(abs(diff(x))), {TS.age},'UniformOutput',0);
        [TS.hasResolution_hasMedianValue] = dat{:};
        dat = cellfun(@(x) nanmean(abs(diff(x))), {TS.age},'UniformOutput',0);
        [TS.hasResolution_hasMeanValue] = dat{:};
        dat = cellfun(@(x) nanmax(abs(diff(x))), {TS.age},'UniformOutput',0);
        [TS.hasResolution_hasMaxValue] = dat{:};
        dat = cellfun(@(x) nanmin(abs(diff(x))), {TS.age},'UniformOutput',0);
        [TS.hasResolution_hasMinValue] = dat{:};
        [TS.hasResolution_units] = TS.ageUnits;
    else
        warning('Some of your year columns are cells, so I cant calculate resolution')
    end
end

delete(h)

if strcmp(mode,'chron')
    %replace all the 'paleo' names with 'chron'
    allnames = fieldnames(TS);
    wp = find(cellfun(@(x) length(x)==1 , regexp(allnames,'paleoData_')));
    for ww = 1:length(wp)
        newname = regexprep(allnames{wp(ww)},'paleoData_','chronData_');
        [TS.(newname)] = TS.(allnames{wp(ww)});
    end
    
    TS = rmfield(TS,allnames(wp));
    
    %deal with special fields. 
    special = {'chronData_paleoName','chronData_paleoNumber'};
    specialReplace = {'chronData_chronName','chronData_chronNumber'};
    for s =1:length(special)
        if isfield(TS,special{s})
           [TS.(specialReplace{s})] =   TS.(special{s});
           TS = rmfield(TS,special{s});
        end
    end
    
    if isfield(TS,'chronData')
        [TS.paleoData] = TS.chronData;
        TS = rmfield(TS,'chronData');
    end
end

TS = structord(TS);%alphabetize

%Remove blacklisted variable names
blacklist = {'paleoData_paleoMeasurementTableNumber','chronData_chronMeasurementTableNumber','paleoData_measurementTableNumber','chronData_measurementTableNumber'};
TS = rmfieldsoft(TS,blacklist);

end

function TS=populateTsRow(PM,L,tableType,paleoNumber,modelNumber,tableNumber)

ts = 0;
% Special columns need to
specialColumns = {'age','year','depth','ageEnsemble'};
allColumns = structFieldNames(PM);

%columnsToGrab = setdiff(allColumns,specialColumns);

% Do not exclude the special columns. We need time series entries for those as well. ALL columns.
columnsToGrab = structFieldNames(PM);

for ctg = 1:length(columnsToGrab) %which columns to grab? These are your timeseries objets
    ts = ts+1;
    
    %%%BASE LEVEL
    excludeBase = {'@context'};
    %    TS(ts).mode = mode;
    
    baseGrab = fieldnames(L);
    
    
    %notStructorCell = find(cellfun(@(x) ~iscell(L.(x)) & ~isstruct(L.(x)),baseGrab))
    notStructorCell = find(~structfun(@iscell,L) & ~structfun(@isstruct,L));
    baseGrab = setdiff(baseGrab(notStructorCell),excludeBase);
    
    for b = 1:length(baseGrab) %assign = needed baselevel stuff
        TS(ts).(baseGrab{b}) = L.(baseGrab{b});
    end
    
    
    %%%PUB
    %NOTE - I'm not currently differentiating between pub and dataPub. NPM 4.17.17
    if isfield(L,'pub')
        for pu = 1:length(L.pub)
            PUB = L.pub{pu};
            if ~isempty(PUB)
                %pull DOI out if needed
                if isfield(PUB,'identifier')
                    if isstruct(PUB.identifier)
                        PUB.DOI = PUB.identifier{1}.id;
                    end
                end
                pubGrab = find(~structfun(@iscell,PUB));%grab everything here that's not a cell
                pubFields = fieldnames(PUB);
                pubFields = pubFields(pubGrab);
                for ppu = 1:length(pubGrab) %assign = needed pub stuff
                    TS(ts).(['pub',num2str(pu),'_',pubFields{ppu}])  = PUB.(pubFields{ppu});
                end
            end
        end
    end
    %END PUB
    
    %%%FUNDING
    if isfield(L,'funding')
        for fu = 1:length(L.funding)
            FU = L.funding{fu};
            funGrab = find(~structfun(@iscell,FU));%grab everything here that's not a cell
            funFields = fieldnames(FU);
            funFields = funFields(funGrab);
            for ffu = 1:length(funFields)%assign = needed funding stuff
                TS(ts).(['funding',num2str(fu),'_',funFields{ffu}])  = FU.(funFields{ffu});
            end
        end
    end
    %END FUNDING
    
    %%%%GEO
    excludeGeo = {'type'};
    geoFields = fieldnames(L.geo);
    geoGrab = setdiff(geoFields,excludeGeo);
    
    for g = 1:length(geoGrab)%assign = needed geo stuff
        TS(ts).(['geo_',geoGrab{g}]) = L.geo.(geoGrab{g});
    end
    
    %%%END GEO
    
    %%PaleoData
    
    %%Paleo data table level
    %assign = paleo and measurementTable Numbers
    TS(ts).paleoData_paleoNumber = paleoNumber;
    TS(ts).paleoData_tableNumber = tableNumber;
    
    if strncmp(tableType,'measurement',11)
        TS(ts).paleoData_tableType = 'measurement';
        %grab metadata from this measurement table
        pal = L.paleoData{paleoNumber}.measurementTable{tableNumber};
    elseif strncmp(tableType,'summary',7)
        TS(ts).paleoData_modelNumber = modelNumber;
        %grab metadata from this summary table
        pal = L.paleoData{paleoNumber}.model{modelNumber}.summaryTable{tableNumber};
        TS(ts).paleoData_tableType = 'summary';
        if isfield(L.paleoData{paleoNumber}.model{modelNumber},'method')
            %populate method metadata ...
            met = L.paleoData{paleoNumber}.model{modelNumber}.method;
            mtfn = fieldnames(met);
            for mmm = 1:length(mtfn)
                thisvar = met.(mtfn{mmm});
                if isstruct(thisvar)
                    error('model method fields cannot be structures')
                end
                if iscell(thisvar)
                    error('model method fields cannot be cells')
                end
                TS(ts).(['method_' mtfn{mmm}]) = thisvar;
            end
        end
    elseif strncmp(tableType,'ens',3)
        TS(ts).paleoData_modelNumber = modelNumber;
        %grab metadata from this ensemble table
        pal = L.paleoData{paleoNumber}.model{modelNumber}.ensembleTable{tableNumber};
        TS(ts).paleoData_tableType = 'ensemble';
    end
    
    %if it's a model table (ensemble or summary) then get model metadata.
    
    
    
    %excludePaleo = {''};
    palFields = fieldnames(pal);
    palGrab = find(~structfun(@isstruct,pal));
    palFields = palFields(palGrab);
    for palp = 1:length(palFields)%assign = needed paleo stuff
        TS(ts).(['paleoData_',palFields{palp}]) = pal.(palFields{palp});
    end
    
    %%Paleodata Column level
    try
        coldata = pal.(columnsToGrab{ctg});
    catch DO
        display('uh oh')
    end
    %grab data and metadata from this column
    excludeColumn = {'number', 'tableName','paleoNumber','chronNumber','paleoDataTableName','measurementTableNumber','measurementTableName','paleoMeasurementTableNumber'};
    colFields = fieldnames(coldata);
    colGrab = find(~structfun(@isstruct,coldata));
    colFields = setdiff(colFields(colGrab),excludeColumn);
    
    for colc = 1:length(colFields)%assign = needed column data and metadata
        if iscell(coldata.(colFields{colc}))
            if all(cellfun(@isstruct,coldata.(colFields{colc})))
                continue
            end
        end
        TS(ts).(['paleoData_',colFields{colc}]) = coldata.(colFields{colc});
    end
    
    
    %look through subsequent lists for hierarchical metadata
    hierStructNames = structFieldNames(coldata);
    %this handles structures at this level
    for hsi = 1:length(hierStructNames)
        HSO = coldata.(hierStructNames{hsi});
        hsNames = fieldnames(HSO);%cant handle anything deeper than this at the moment
        for hssi =1:length(hsNames)
            TS(ts).([hierStructNames{hsi} '_' hsNames{hssi}]) = HSO.(hsNames{hssi});
        end
    end
    
    %this looks for cells
    hierCellNames = fieldnames(coldata);
    hierCellNames = hierCellNames(structfun(@iscell, coldata));
    
    %
    
    %loop through all of these.
    for hi = 1:length(hierCellNames) % this handles numbered instances (like interpretation) at the second level...
        thisHierData = coldata.(hierCellNames{hi});
        if all(cellfun(@isstruct,thisHierData))
            for hii = 1:length(thisHierData)
                thdNames = fieldnames(thisHierData{hii});
                %thdNames = thdNames(~structfun(@iscell, thisHierData{hii}) & ~structfun(@isstruct, thisHierData{hii}));
                if any(structfun(@iscell, thisHierData{hii}) | structfun(@isstruct, thisHierData{hii}))
                    warning([L.dataSetName ': has structures or cell in a cell at the sub-column level. This is beyond current capacity'])
                end
                for hieri = 1:length(thdNames)
                    %assign = non lists
                    TS(ts).([hierCellNames{hi} num2str(hii) '_' thdNames{hieri}]) = thisHierData{hii}.(thdNames{hieri});
                end
                
            end %end hii loop
        end %cell check if statement
    end %end hi loop
    
    %now special columns
    specCols = specialColumns(find(ismember(specialColumns,structFieldNames(PM))));
    for sc = 1:length(specCols)
        if isfield( PM.(specCols{sc}),'units')
            %only assign = values and units for now
            TS(ts).([specCols{sc} 'Units']) = PM.(specCols{sc}).units;
        else
            TS(ts).([specCols{sc} 'Units']) = 'missing!';
        end
        TS(ts).([specCols{sc}]) = PM.(specCols{sc}).values;
    end
    
    %%END PALEODATA!! Woohoo!
    
    % Raw chronData
    %TS(ts).raw = L; %Now just store the whole structure in there.
    
    if isfield(L,'chronData')
        TS(ts).chronData = L.chronData;
    end
    % if(any(names(L)=='chronData')){
    %   TS(ts)['chronData'] = L.chronData
    % }
    % % Raw paleoData
    % TS(ts)['paleoData'] = L.paleoData
    
end %columns to grab (each TS entry)
end

