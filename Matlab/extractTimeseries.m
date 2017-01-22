
function TS=extractTimeseries(D,allColumns)

%extract timeseries
%iteratively go through columns, adding year/value pairs and metadata to
%rows in a structure

if nargin <2
    %assume that we don't want age,year or depth include
    allColumns=0;
end

%is it a database, or a LiPD Hierarchical object?
if isfield(D,'dataSetName')
    %then make it a database
    D=struct(makeValidName(D.dataSetName),D);
end
dnames=fieldnames(D);
%start at database level
ts=1;
for d=1:length(fieldnames(D)) %for every paleoarchive in database
    
    ppnames=fieldnames(D.(dnames{d})); % get PP level fieldnames
    
    %change for 1.2: pull all paleoMeasurmentTables to front. Name/Number
    %appropriately.
    for pd=1:length(D.(dnames{d}).paleoData)
        PD=D.(dnames{d}).paleoData{pd};
        for pds= 1:length(PD)
            if ~isfield(PD.paleoMeasurementTable{pds},'paleoDataTableName')
                PD.paleoMeasurementTable{pds}.paleoDataTableName=['data' num2str(pds)];
            end
            
            if pd==1 & pds==1
                pdname = [PD.paleoMeasurementTable{pds}.paleoDataTableName];
            else
                pdname = makeUniqueStrings([PD.paleoMeasurementTable{pds}.paleoDataTableName],structFieldNames(D.(dnames{d}).paleoMeasurementTable));
            end
            
            D.(dnames{d}).paleoMeasurementTable.(pdname) = PD.paleoMeasurementTable{pds};
            D.(dnames{d}).paleoMeasurementTable.(pdname).paleoNumber = pd;
            D.(dnames{d}).paleoMeasurementTable.(pdname).paleoMeasurementTableNumber = pds;
            
            
        end
    end
    
    %THIS IS HACKY. Do better nick.
    D.(dnames{d}).paleoDataFull =  D.(dnames{d}).paleoData;
    D.(dnames{d}).paleoData= D.(dnames{d}).paleoMeasurementTable;
    
    
    
    
    %make it so that paleoData is last
    measnamei=find(strcmp('paleoData',ppnames));
    sti=[setdiff(1:length(ppnames),measnamei) measnamei];
    ppnames=ppnames(sti);
    
    % badPaleoi=find(strcmp('paleoMeasurementTable',ppnames) | strcmp('paleoDataFull',ppnames));
    
    
    
    
    %deal with chronData.
    
    chroni=find(strcmp('chronData',ppnames));
    if ~isempty(chroni)
        %for now, store all of chrondata in each TS struct.
        %in the future - consider linking specific chron tables to
        %appropriate paleodata tables
        TS(1,ts).chronData=D.(dnames{d}).chronData;
        
        %now remove chrondata from list
        cti=setdiff(1:length(ppnames),chroni);
        ppnames=ppnames(cti);
    end
    
    TS(1,ts).dataSetName=dnames{d}; %assign in name
    
    for pp=1:length(ppnames) %go through all the fields in the LiPD object
        %special case for pub
        if strcmp(ppnames{pp},'pub')
            dpn=1;
            pubnum=1;
            pflag=0;
            dcflag=0;
            for pl=1:length( D.(dnames{d}).pub)
                if isstruct(D.(dnames{d}).pub{pl})
                    if dcflag
                        dpn=dpn+1;
                    end
                    if pflag
                        pubnum=pubnum+1;
                    end
                    pflag=0;
                    dcflag=0;
                    
                    pubNames=fieldnames(D.(dnames{d}).pub{pl});
                    
                    for pn=1:length(pubNames)
                        if any(strcmp('type',pubNames))
                            if strcmp(D.(dnames{d}).pub{pl}.type,'dataCitation')
                                TS(1,ts).(['dataPub' num2str(dpn) '_' pubNames{pn}])=D.(dnames{d}).pub{pl}.(pubNames{pn});
                                dcflag=1;
                            else
                                TS(1,ts).([ppnames{pp} num2str(pl) '_' pubNames{pn}])=D.(dnames{d}).pub{pl}.(pubNames{pn});
                                pflag=1;
                            end
                        else
                            TS(1,ts).([ppnames{pp} num2str(pl) '_' pubNames{pn}])=D.(dnames{d}).pub{pl}.(pubNames{pn});
                            pflag=1;
                            
                        end
                    end
                end
            end
            %special case for funding
        elseif strcmp(ppnames{pp},'funding')
            for pl=1:length( D.(dnames{d}).funding)
                if isstruct(D.(dnames{d}).funding{pl})
                    
                    fundNames=fieldnames(D.(dnames{d}).funding{pl});
                    for pn=1:length(fundNames)
                        TS(1,ts).([ppnames{pp} num2str(pl) '_' fundNames{pn}])=D.(dnames{d}).funding{pl}.(fundNames{pn});
                    end
                end
            end
            
        else
            
            if ~isstruct(D.(dnames{d}).(ppnames{pp})) %for each non structure in paleoArchive assign to column
                TS(1,ts).(ppnames{pp})=D.(dnames{d}).(ppnames{pp});
            else %it is a structure at the PP level
                l3names=fieldnames(D.(dnames{d}).(ppnames{pp}));
                for l3=1:length(l3names)
                    %store TS line when l3=1 so we can replicate if l3>1
                    if pp==length(ppnames)
                        if l3==1
                            Tstempl3=TS(1,ts);
                            ts3=ts;
                        elseif l3>1 & ts~=ts3
                            %create new empty fields
                            oldfn=fieldnames(Tstempl3);
                            newfn=fieldnames(TS(1,ts-1));
                            %changefn=setdiff(newfn,oldfn);
                            changefn=newfn(length(oldfn)+1:end);
                            C = reshape(changefn, 1, []); %// Field names
                            C(2, :) = {[]};               %// Empty values
                            TS(1,ts)=mergestruct(Tstempl3,struct(C{:}));
                            %TS(1,ts)=Tstempl3;
                        end
                    end
                    
                    if ~isstruct(D.(dnames{d}).(ppnames{pp}).(l3names{l3}))
                        TS(1,ts).([ppnames{pp} '_' l3names{l3}])=D.(dnames{d}).(ppnames{pp}).(l3names{l3});
                    else
                        l4names=fieldnames(D.(dnames{d}).(ppnames{pp}).(l3names{l3}));
                        
                        if ~strcmp(ppnames{pp},'paleoData')
                            for l4=1:length(l4names)
                                if ~isstruct(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4names{l4}))
                                    TS(1,ts).([ppnames{pp} '_' l3names{l3} '_' l4names{l4}])=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4names{l4});
                                else
                                    l5names=fieldnames(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4names{l4}));
                                    for l5=1:length(l5names)
                                        if ~isstruct(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4names{l4}).(l5names{l5}))
                                            if isfield(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4names{l4}),l5names{l5})
                                                TS(1,ts).([ppnames{pp} '_' l3names{l3} '_' l4names{l4} '_' l5names{l5}])=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4names{l4}).(l5names{l5});
                                            end
                                        else
                                            'really, you have structures at L5?'
                                            
                                        end
                                    end
                                end
                            end
                            
                            %what do with the paleoData structure
                        elseif strcmp(ppnames{pp},'paleoData')
                            clear age* year* depth*
                            yearFlag=0;
                            ageFlag=0;
                            depthFlag=0;
                            l4structs=structFieldNames(D.(dnames{d}).(ppnames{pp}).(l3names{l3}));
                            l4nonStructs=setdiff(fieldnames(D.(dnames{d}).(ppnames{pp}).(l3names{l3})),l4structs);
                            %go through the nonStructs and write them in
                            for l4n=1:length(l4nonStructs)
                                TS(1,ts).([ppnames{pp} '_' l4nonStructs{l4n}])=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4nonStructs{l4n});
                            end
                            
                            
                            for l4=1:length(l4structs)
                                %TS(1,ts).paleoDataTableName=l3names{l3};
                                %store TS line when l3=1 so we can replicate if l3>1
                                if l4==1
                                    Tstempl4=TS(1,ts);
                                    ts4=ts;
                                elseif l4>1 & ts~=ts4
                                    TS(1,ts)=Tstempl4;
                                end
                                %first find years and ages and depth
                                if any(strcmpi('year',l4structs{l4})) %year field, write to year
                                    yearFlag=1;
                                    yeari=l4;
                                    if ~isfield(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{l4}),'values')
                                        error([dnames{d} '.' ppnames{pp} '.' l3names{l3} '.' l4structs{l4} ' is missing values'])
                                    end
                                    year=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{l4}).values;
                                    if isfield(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{l4}),'units')
                                        yearUnits=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{l4}).units;
                                    else
                                        yearUnits='AD (guessed based on variableName)';
                                    end
                                end
                                if  any(strcmpi('age',l4structs{l4})) %age field, write to age
                                    ageFlag=1;
                                    agei=l4;
                                    age=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{l4}).values;
                                    if isfield(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{l4}),'units')
                                        ageUnits=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{l4}).units;
                                    else
                                        ageUnits='BP (guessed based on variableName)';
                                    end
                                end
                                if  any(strcmpi('depth',l4structs{l4})) %depth field, write to depth
                                    depthFlag=1;
                                    depthi=l4;
                                    depth=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{l4}).values;
                                    if isfield(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{l4}),'units')
                                        depthUnits=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{l4}).units;
                                    else
                                        depthUnits = 'unknown';
                                    end
                                end
                            end
                            nonAgeCol=1:length(l4structs);

                            if yearFlag & ageFlag
                                nonAgeCol=setdiff(nonAgeCol,[yeari agei]);
                                
                            elseif yearFlag
                                nonAgeCol=setdiff(nonAgeCol,[yeari]);
                            elseif ageFlag
                                nonAgeCol=setdiff(nonAgeCol,[agei]);
                                
                            elseif ~depthFlag
                                display(l4structs)
                                warning([dnames{d} ': ' l3names{l3} ': there dont appear to be any year or age columns. Skipping..'])
                                continue
                                
                            end
                            
                            %exclude depth too
                            if depthFlag
                                nonAgeCol=setdiff(nonAgeCol,[depthi]);
                            end
                            
                            if allColumns%optionally, export all columns
                                nonAgeCol=1:length(l4structs);
                            end
                                for nAC=1:length(nonAgeCol)
                                    %store TS line when l3=1 so we can replicate if l3>1
                                    if nAC==1
                                        TstempnAC=TS(1,ts);
                                        tsAC=ts;
                                    elseif nAC>1 & tsAC~=ts
                                        %create new empty fields
                                        oldfn=fieldnames(TstempnAC);
                                        newfn=fieldnames(TS(1,ts-1));
                                        %changefn=setdiff(newfn,oldfn);
                                        changefn=newfn(length(oldfn)+1:end);
                                        C = reshape(changefn, 1, []); %// Field names
                                        C(2, :) = {[]};                    %// Empty values
                                        TS(1,ts)=mergestruct(TstempnAC,struct(C{:}));
                                    end
                                    %currently can't handle non-structure
                                    %fields at this level! Need to test for
                                    %structures and write those first
                     
                                    if isstruct(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{nonAgeCol(nAC)})) %write non structure fields in column
                                        %write age/year fields
                                        if ageFlag
                                            TS(1,ts).age=age;
                                            TS(1,ts).ageUnits=ageUnits;
                                        end
                                        if yearFlag
                                            TS(1,ts).year=year;
                                            TS(1,ts).yearUnits=yearUnits;
                                        end
                                        if depthFlag
                                            TS(1,ts).depth=depth;
                                            TS(1,ts).depthUnits=depthUnits;
                                        end
                                        l5names=fieldnames(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{nonAgeCol(nAC)}));
                                        for l5=1:length(l5names)
                                            %write paleoData fields
                                            l5name=l5names{l5};
                                            if isstruct(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{nonAgeCol(nAC)}))%if it's a data column, not metadata
                                                %determine whether it's a
                                                %structure( like climate
                                                %interp)
                                                if isstruct(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{nonAgeCol(nAC)}).(l5name))%if it's a structure
                                                    l6names=fieldnames(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{nonAgeCol(nAC)}).(l5name));
                                                    
                                                    for l6 = 1:length(l6names)
                                                        l6name=l6names{l6};
                                                        if ~iscell(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{nonAgeCol(nAC)}).(l5names{l5}).(l6names{l6}))
                                                            TS(1,ts).([l5name '_' l6name])=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{nonAgeCol(nAC)}).(l5names{l5}).(l6names{l6});
                                                        else
                                                            %append a number and loop through cell
                                                            for iiii = 1:length(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{nonAgeCol(nAC)}).(l5names{l5}).(l6names{l6}));
                                                                l7names = fieldnames(D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{nonAgeCol(nAC)}).(l5names{l5}).(l6names{l6}){iiii});
                                                                for l7 = 1:length(l7names)
                                                                    TS(1,ts).([l5name '_' l6name num2str(iiii) '_' l7names{l7}])=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{nonAgeCol(nAC)}).(l5names{l5}).(l6names{l6}){iiii}.(l7names{l7});
                                                                end
                                                            end
                                                        end
                                                    end
                                                else %not a structure, write out the data
                                                    TS(1,ts).(['paleoData_' l5name])=D.(dnames{d}).(ppnames{pp}).(l3names{l3}).(l4structs{nonAgeCol(nAC)}).(l5names{l5});
                                                end
                                            end
                                        end
                                        ts=ts+1;
                                    end
                                end
                            
                        end
                    end
                end
            end
        end
        
        
        
        
        
    end
    
    
end
if isfield(TS,'paleoData_tableName')
    TS=rmfield(TS,'paleoData_tableName');
end
TS=structord(TS);








