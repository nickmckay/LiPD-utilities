function Dnew=collapseTS(TS,yearTS)
% tries to convert a LiPD Timeseries object back into a LiPD Hierarchical
% object
% TS is the TS structure
% yearTS is an optional flag to tripped if your TS includes entries for
% year/age/etc


% %% TO DO
% 1. Add chron mode
% 2. handle model methods...

if nargin<2
    yearTS=1;
end

%create a LiPD object for every unique dataSetName
udsn=unique({TS.dataSetName}');
handle = waitbar(0,'Collapsing timeseries...');

for i=1:length(udsn)
    
    waitbar(i/length(udsn),handle);
    %find TS entries that match that unique Name
    fts=find(strcmp(udsn{i},{TS.dataSetName}'));
    
    for f=1:length(fts) %make a paleoDataTable entry for each TS
        T=TS(fts(f));
        T=removeEmptyStructureFields(T);
        fT=fieldnames(T);
        
        
        %only do this for the first entry for base level stuff.
        if f==1
            %base level
            %all the fields that don't have underscores (except year and age)
            b=find(cellfun(@isempty,(strfind(fT,'_'))));
            yi=find(strncmpi('year',fT,4));
            ai=find(strncmpi('age',fT,3));
            yai=union(ai,yi);
            %or depth
            di=find(strncmpi('depth',fT,5));
            yai=union(yai,di);
            
            %or chronData
            ci=find(strcmpi('chronData',fT));
            yai=union(yai,ci);
            
            %if there is a chronData, write it right in
            if ~isempty(ci)
                Dnew.(makeValidName(udsn{i})).chronData=T.chronData;
            elseif isfield(T,'raw')
                if isfield(T.raw,'chronData')
                    Dnew.(makeValidName(udsn{i})).chronData=T.raw.chronData;
                end
            end
            
            %now create the base level index
            b=setdiff(b,yai);
            
            for bi=1:length(b)
                Dnew.(makeValidName(udsn{i})).(fT{b(bi)})=T.(fT{b(bi)});
            end
            
            %funding
            fun=find(strncmp('funding',fT,7));
            if numel(fun)>0
                Dnew.(makeValidName(udsn{i})).funding=cell(1,1); %assign cell to funding
                for fin=1:length(fun)
                    funVarName=fT{fun(fin)};
                    fundNum=str2num(funVarName(8:(strfind(funVarName,'_')-1)));
                    if isempty(fundNum)
                        fundNum=1;
                    end
                    try
                        Dnew.(makeValidName(udsn{i})).funding{fundNum}.(funVarName(strfind(funVarName,'_')+1:end))=T.(fT{fun(fin)});
                    catch DO
                        Dnew.(makeValidName(udsn{i})).funding{fundNum}.(funVarName(strfind(funVarName,'_')+1:end))=char(T.(fT{fun(fin)}));
                    end
                end
            end
            
            %pub
            clear pubNum %so that we don't get a bajillion dataPubs
            if f==1
                Dnew.(makeValidName(udsn{i})).pub=cell(1,1); %assign cell to pub
            end
            p=find(strncmp('pub',fT,3));
            for pin=1:length(p)
                pubVarName=fT{p(pin)};
                pubNum=str2num(pubVarName(4:(strfind(pubVarName,'_')-1)));
                if isempty(pubNum)
                    pubNum=1;
                end
                %don't overwrite what you've already written
                if length(Dnew.(makeValidName(udsn{i})).pub) < pubNum % if this is a new publication
                    %write it
                    Dnew.(makeValidName(udsn{i})).pub{pubNum}.(pubVarName(strfind(pubVarName,'_')+1:end))=...
                        T.(fT{p(pin)});
                elseif ~isfield(Dnew.(makeValidName(udsn{i})).pub{pubNum},pubVarName(strfind(pubVarName,'_')+1:end))
                    %write it
                    Dnew.(makeValidName(udsn{i})).pub{pubNum}.(pubVarName(strfind(pubVarName,'_')+1:end))=...
                        T.(fT{p(pin)});
                elseif isempty(Dnew.(makeValidName(udsn{i})).pub{pubNum}.(pubVarName(strfind(pubVarName,'_')+1:end)))
                    %if it's empty
                    %write it.
                    Dnew.(makeValidName(udsn{i})).pub{pubNum}.(pubVarName(strfind(pubVarName,'_')+1:end))=...
                        T.(fT{p(pin)});
                end
            end
            
            %         %assign in something in case there's no other publications
            %         if(~exist('pubNum'))
            %             lastPub=0;
            %         else
            %             lastPub=pubNum;
            %         end
            
            
            %make all data pubs start at 20
            lastPub = 20;
            
            %handle Data citations
            dp=find(strncmp('dataPub',fT,7));
            for dpin=1:length(dp)
                pubVarName=fT{dp(dpin)};
                pubNum=lastPub+str2num(pubVarName(8:(strfind(pubVarName,'_')-1)));
                %don't overwrite what you've already written
                if length(Dnew.(makeValidName(udsn{i})).pub) < pubNum % if this is a new publication
                    %write it
                    Dnew.(makeValidName(udsn{i})).pub{pubNum}.(pubVarName(strfind(pubVarName,'_')+1:end))=T.(fT{dp(dpin)});
                elseif ~isfield(Dnew.(makeValidName(udsn{i})).pub{pubNum},pubVarName(strfind(pubVarName,'_')+1:end)) %it's a new variable
                    %write it
                    Dnew.(makeValidName(udsn{i})).pub{pubNum}.(pubVarName(strfind(pubVarName,'_')+1:end))=T.(fT{dp(dpin)});
                elseif isempty(Dnew.(makeValidName(udsn{i})).pub{pubNum}.(pubVarName(strfind(pubVarName,'_')+1:end)))
                    %if it's empty
                    %write it.
                    Dnew.(makeValidName(udsn{i})).pub{pubNum}.(pubVarName(strfind(pubVarName,'_')+1:end))=T.(fT{dp(dpin)});
                end
            end
            
            
            
            %geo
            if f==1
                Dnew.(makeValidName(udsn{i})).geo=struct; %assign geo to structure
            end
            g=find(strncmp('geo_',fT,4));
            
            for gin=1:length(g)
                geoVarName=fT{g(gin)};
                
                Dnew.(makeValidName(udsn{i})).geo.(geoVarName(strfind(geoVarName,'_')+1:end))=...
                    T.(fT{g(gin)});
            end
            
            
            %paleoData
            Dnew.(makeValidName(udsn{i})).paleoData=cell(1,1); %assign paleoData to a  cell
        end
        pd=find(strncmp('paleoData_',fT,10));
        
        %get or create the name of the relevant paleodata table
        if isfield(T,'paleoData_paleoNumber')
            if ischar(T.paleoData_paleoNumber)
                T.paleoData_paleoNumber = str2num(T.paleoData_paleoNumber);
            end
            pnum = T.paleoData_paleoNumber;
        else
            %assume its 1
            pnum = 1;
        end
        %check to see if the number is str
        if ischar(pnum)
            pnum = str2num(pnum);
            T.paleoData_paleoNumber = pnum;
        end
        
        if isfield(T,'paleoData_modelNumber')
            modnum = T.paleoData_modelNumber;
        else
            modnum = 1;
        end
        
        if isfield(T,'paleoData_tableNumber')
            mnum = T.paleoData_tableNumber;
        else
            if isfield(T,'paleoData_paleoMeasurementTableNumber') & isfield(T,'paleoData_measurementTableNumber')
                if ischar(T.paleoData_paleoMeasurementTableNumber)
                    T.paleoData_paleoMeasurementTableNumber = str2num(T.paleoData_paleoMeasurementTableNumber);
                end
                mnum1 = T.paleoData_paleoMeasurementTableNumber;
                if ischar(T.paleoData_measurementTableNumber)
                    T.paleoData_measurementTableNumber = str2num(T.paleoData_measurementTableNumber);
                end
                mnum2 = T.paleoData_measurementTableNumber;
                
                mnum = max([mnum1 mnum2]);
                T.paleoData_measurementTableNumber = mnum;
            elseif isfield(T,'paleoData_paleoMeasurementTableNumber')
                
                if ischar(T.paleoData_paleoMeasurementTableNumber)
                    T.paleoData_paleoMeasurementTableNumber = str2num(T.paleoData_paleoMeasurementTableNumber);
                end
                mnum = T.paleoData_paleoMeasurementTableNumber;
                T.paleoData_measurementTableNumber = mnum;
                T = rmfield(T,'paleoData_paleoMeasurementTableNumber');
            elseif isfield(T,'paleoData_measurementTableNumber')
                
                if ischar(T.paleoData_measurementTableNumber)
                    T.paleoData_measurementTableNumber = str2num(T.paleoData_measurementTableNumber);
                end
                mnum = T.paleoData_measurementTableNumber;
            else
                %assume its 1
                mnum = 1;
            end
            
        end
        %check to see if the number is str
        if ischar(mnum)
            mnum = str2num(mnum);
            T.paleoData_tableNumber = mnum;
        end
        
        T = rmfieldsoft(T,{'paleoData_paleoMeasurementTableNumber','paleoData_measurementTableNumber'});
        
        %get table type
        if isfield(T,'paleoData_tableType')
            tableType = T.paleoData_tableType;
        else
            tableType = 'measurement';
        end
        
        
        %create empty table
        if length(Dnew.(makeValidName(udsn{i})).paleoData) < pnum
            Dnew.(makeValidName(udsn{i})).paleoData{pnum} = struct;
        end
        
        
        switch lower(tableType(1:4))
            case 'meas'
                if ~isfield(Dnew.(makeValidName(udsn{i})).paleoData{pnum},'measurementTable')
                    Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}=struct;
                end
            case 'summ'
                if ~isfield(Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum},'summaryTable')
                    Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}=struct;
                end
            otherwise
                error('dont recognize table type')
        end
        
        switch lower(tableType(1:4))
            case 'meas'
                if length(Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable) < mnum
                    Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}=struct;
                end
            case 'summ'
                if length(Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable) < mnum
                    Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}=struct;
                end
            otherwise
                error('dont recognize table type')
        end
        
        
        
        
        %which variables should be at the measurement table level?
        amt = {'paleoDataTableName','tableName',...
            'paleoDataMD5',...
            'googleWorkSheetKey'};
        
        for am =1:length(amt)
            if any(strcmp(['paleoData_' amt{am}],fT))
                switch lower(tableType(1:4))
                    case 'meas'
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.(amt{am})=T.(['paleoData_' amt{am}]);
                    case 'summ'
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.(amt{am})=T.(['paleoData_' amt{am}]);
                    otherwise
                        error('dont recognize table type')
                end
                pd=setdiff(pd,find(strcmp(fT,['paleoData_' amt{am}])));
            end
            
        end
        
        
        
        %get variablename name
        variableName=makeValidName(T.paleoData_variableName);
        %         if iscell(variableName)
        %             variableName=variableName{1};
        %         end
        %see if that name has been used already
        switch lower(tableType(1:4))
            case 'meas'
                alreadyNames=fieldnames(Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum});
            case 'summ'
                alreadyNames=fieldnames(Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum});
        end
        %iterate through numbers until it's unique
        aNi=1;
        origName=variableName;
        while any(strcmp(variableName,alreadyNames))
            variableName=[origName num2str(aNi)];
            aNi=aNi+1;
        end
        
        
        
        %add in the variable
        dontAdd = {'paleoData_paleoMeasurementTableNumber','paleoData_measurementTableNumber',...
            'paleoData_number','paleoData_paleoNumber','paleoData_tableNumber','paleoData_modelNumber',...
            'paleoData_tableType'};
        for pdin=1:length(pd)
            pdVarName=fT{pd(pdin)};
            if ~any(strcmp(pdVarName,dontAdd));
                %add in parameter
                switch lower(tableType(1:4))
                    case 'meas'
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.(variableName).(pdVarName(strfind(pdVarName,'_')+1:end))=T.(fT{pd(pdin)});
                    case 'summ'
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.(variableName).(pdVarName(strfind(pdVarName,'_')+1:end))=T.(fT{pd(pdin)});
                    otherwise
                        error('dont recognize table type')
                end
                
            end
        end
        
        
        if yearTS % if years are included as TS entries do something new
            
            
        else
            %add year as a column
            yearFlag=0;
            if any(strcmp('year',fT))
                if length(T.year) == length(T.paleoData_values)
                    switch lower(tableType(1:4))
                        case 'meas'
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.year.TSid=[makeValidName(udsn{i}) 'paleo' num2str(pnum) 'meas' num2str(mnum) 'year'];
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.year.values=T.year;
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.year.units='AD';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.year.description='Year AD';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.year.variableName='year';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.year.dataType='float';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.year.variableType='inferred';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.year.inferredVariableType='year';
                        case 'summ'
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.year.TSid=[makeValidName(udsn{i}) 'paleo' num2str(pnum) 'sum' num2str(mnum) 'year'];
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.year.values=T.year;
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.year.units='AD';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.year.description='Year AD';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.year.variableName='year';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.year.dataType='float';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.year.variableType='inferred';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.year.inferredVariableType='year';
                    end
                    yearFlag=1;
                end
            end
            %add age as column
            ageFlag=0;
            if any(strcmp('age',fT))
                %don't add age if it's a different length than the data
                if length(T.age) == length(T.paleoData_values)
                    switch lower(tableType(1:4))
                        case 'meas'
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.age.TSid=[makeValidName(udsn{i}) 'paleo' num2str(pnum) 'meas' num2str(mnum) 'age'];
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.age.values=T.age;
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.age.units='BP';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.age.description='Years before present (1950) BP';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.age.variableName='age';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.age.dataType='float';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.age.variableType='inferred';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.age.inferredVariableType='age';
                        case 'summ'
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.age.TSid=[makeValidName(udsn{i}) 'paleo' num2str(pnum) 'sum' num2str(mnum) 'age'];
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.age.values=T.age;
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.age.units='BP';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.age.description='Years before present (1950) BP';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.age.variableName='age';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.age.dataType='float';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.age.variableType='inferred';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.age.inferredVariableType='age';
                    end
                    
                    ageFlag=1;
                end
            end
            %add depth as column
            depthFlag=0;
            if any(strcmp('depth',fT))
                %don't add age if it's a different length than the data
                if length(T.depth) == length(T.paleoData_values)
                    switch lower(tableType(1:4))
                        case 'meas'
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.depth.TSid=[makeValidName(udsn{i}) 'paleo' num2str(pnum) 'meas' num2str(mnum) 'depth'];
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.depth.values=T.depth;
                            if isfield(T,'depthUnits')
                                Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.depth.units=T.depthUnits;
                            end
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.depth.description='depth';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.depth.variableName='depth';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.depth.dataType='float';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.depth.variableType='measured';
                        case 'summ'
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.depth.TSid=[makeValidName(udsn{i}) 'paleo' num2str(pnum) 'sum' num2str(mnum) 'depth'];
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.depth.values=T.depth;
                            if isfield(T,'depthUnits')
                                Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.depth.units=T.depthUnits;
                            end
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.depth.description='depth';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.depth.variableName='depth';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.depth.dataType='float';
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.depth.variableType='measured';
                    end
                    depthFlag=1;
                end
            end
            if ~ageFlag && ~yearFlag && ~depthFlag
                
                error([makeValidName(udsn{i}) ': ' num2str(fts(f)) ': no age, year or depth data. The linearity (and existence) of time (or depth) are necessary assumptions in the LiPD framework | a likely problem is that the length of the data does not match the length of the year and/or age vectors'])
            end
        end
        
        %check for calibration
        if any(strncmp('calibration_',fT,12))
            cai=find(strncmp('calibration_',fT,12));
            for cain=1:length(cai)
                caiVarName=fT{cai(cain)};
                switch lower(tableType(1:4))
                    case 'meas'
                        %add in parameter
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.(variableName).calibration.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                            T.(fT{cai(cain)});
                    case 'summ'
                        %add in parameter
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.(variableName).calibration.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                            T.(fT{cai(cain)});
                end
            end
        end
        
        %check for modernSystem
        if any(strncmp('modernSystem_',fT,13))
            cai=find(strncmp('modernSystem_',fT,13));
            for cain=1:length(cai)
                caiVarName=fT{cai(cain)};
                
                %add in parameter
                switch lower(tableType(1:4))
                    case 'meas'
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.(variableName).modernSystem.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                            T.(fT{cai(cain)});
                    case 'summ'
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.(variableName).modernSystem.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                            T.(fT{cai(cain)});
                end
            end
        end
        
        
        %check for proxySystemModel
        if any(strncmp('proxySystemModel_',fT,17))
            cai=find(strncmp('proxySystemModel_',fT,17));
            for cain=1:length(cai)
                caiVarName=fT{cai(cain)};
                
                %add in parameter
                switch lower(tableType(1:4))
                    case 'meas'
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.(variableName).proxySystemModel.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                            T.(fT{cai(cain)});
                    case 'summ'
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.(variableName).proxySystemModel.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                            T.(fT{cai(cain)});
                end
            end
        end
        
        %check for hasResolution
        if any(strncmp('hasResolution_',fT,14))
            cai=find(strncmp('hasResolution_',fT,14));
            for cain=1:length(cai)
                caiVarName=fT{cai(cain)};
                
                %add in parameter
                switch lower(tableType(1:4))
                    case 'meas'
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.(variableName).hasResolution.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                            T.(fT{cai(cain)});
                    case 'summ'
                        Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.(variableName).hasResolution.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                            T.(fT{cai(cain)});
                end
            end
        end
        
        %check for interpretation
        if any(strncmp('interpretation',fT,14))
            intnum = cellfun(@(x) x(regexp(x,'interpretation[0-9]','end')), fT,'UniformOutput',0);
            %             intnumu = uniqueCell(intnum);
            %             nInterp = max(cellfun(@str2num, intnumu(2:end)));%how many interpretations?
            
            
            
            iii=find(~cellfun(@isempty,intnum));
            for iiin=1:length(iii)
                iiiVarName=fT{iii(iiin)};
                thisIntNum = str2double(intnum(iii(iiin)));
                iiname = iiiVarName(min(strfind(iiiVarName,'_'))+1:end);
                
                if ~isempty(T.(iiiVarName))
                    switch lower(tableType(1:4))
                        case 'meas'
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.measurementTable{mnum}.(variableName).interpretation{thisIntNum}.(iiname)=...
                                T.(iiiVarName);
                        case 'summ'
                            Dnew.(makeValidName(udsn{i})).paleoData{pnum}.model{modnum}.summaryTable{mnum}.(variableName).interpretation{thisIntNum}.(iiname)=...
                                T.(iiiVarName);
                    end
                end
            end
        end
        
    end
    
    %remove empty pub cells
    Dnew.(makeValidName(udsn{i}))=removeEmptyPub(Dnew.(makeValidName(udsn{i})));
    
    %remove raw
    Dnew.(makeValidName(udsn{i}))=rmfieldsoft(Dnew.(makeValidName(udsn{i})),'raw');
    
    
end

df=fieldnames(Dnew);
if length(df)==1
    Dnew=Dnew.(df{1});
end

delete(handle);

