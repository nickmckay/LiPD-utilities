function TS = extractTs(D,chron)


ts=0
mode = 'paleo';
if nargin > 1
    if chron
        mode = 'chron';
    end
end

breakFlag=0;
dsn = structFieldNames(D);
h = waitbar(0,'Extracting your timeseries...');

for d = 1:length(dsn)
    waitbar(d/length(dsn),h);
    
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
    
    % dataSetName not provided. Exit(1), we can't continue without it.
    if ~isfield(L,'paleoData')
        error([dsn{d} ' has no paleoData. This is forbidden.'])
    end
    
    %Loop through paleoData objects
    for p = 1:length(L.paleoData)
        %Loop through paleoMeasurementTables
        for pm = 1:length(L.paleoData{p}.measurementTable)
            PM = L.paleoData{p}.measurementTable{pm};%grab this measurmentTable
            
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
                TS(ts).mode = mode;
                
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
                TS(ts).paleoData_paleoNumber = p;
                TS(ts).paleoData_measurementTableNumber = pm;
                
                %grab metadata from this measurement table
                pal = L.paleoData{p}.measurementTable{pm};
                %excludePaleo = {''};
                palFields = fieldnames(pal);
                palGrab = find(~structfun(@isstruct,pal));
                palFields = palFields(palGrab);
                for palp = 1:length(palFields)%assign = needed paleo stuff
                    TS(ts).(['paleoData_',palFields{palp}]) = pal.(palFields{palp});
                end
                
                %%Paleodata Column level
                coldata = pal.(columnsToGrab{ctg});
                
                %grab data and metadata from this column
                excludeColumn = {'number', 'tableName'};
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
                TS(ts).raw = L; %Now just store the whole structure in there.
                
                
                % if(any(names(L)=='chronData')){
                %   TS(ts)['chronData'] = L.chronData
                % }
                % % Raw paleoData
                % TS(ts)['paleoData'] = L.paleoData
                
            end %columns to grab (each TS entry)
            
        end %loop through paleo measurement tables
    end %loop through paleoData objects
    
    
    
    
end
delete(h)
TS = structord(TS);%alphabetize



