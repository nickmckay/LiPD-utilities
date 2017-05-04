function Dnew=collapseTS(TS,yearTS)
%tries to convert a LiPD Timeseries object back into a LiPD Hierarchical
%object
%TS is the TS structure
%yearTS is an optional flag to tripped if your TS includes entries for
%year/age/etc

if nargin<2
    yearTS=0;
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
        if f==1
            Dnew.(makeValidName(udsn{i})).paleoData=struct; %assign paleoData to structure
        end
        pd=find(strncmp('paleoData_',fT,10));
        
        %get or create the name of the relevant paleodata table
        if isfield(T,'paleoData_tableName')
            
            pdName=T.paleoData_tableName;
            TS(fts(f)).paleoData_paleoDataTableName=pdName;
            
        elseif isfield(T,'paleoData_paleoDataTableName')
            pdName=T.paleoData_paleoDataTableName;
            
        elseif isfield(T,'paleoData_paleoNumber') & isfield(T,'paleoData_paleoMeasurementTableNumber')
            pdName =['pt' num2str(T.paleoData_paleoNumber) '_'  num2str(T.paleoData_paleoMeasurementTableNumber)] ;
            TS(fts(f)).paleoData_paleoDataTableName=pdName;
            T.paleoData_paleoDataTableName=pdName;
            
            
        else
            pdName='s1';
            T.paleoData_paleoDataTableName='s1';
            TS(fts(f)).paleoData_paleoDataTableName=pdName;
            
        end
        
        
        
      

            
        samei=find(strcmp(udsn{i},{TS.dataSetName}') & strcmp(pdName,{TS.paleoData_paleoDataTableName}'));
        if length(samei)>1
            clear dll
            for dl=1:length(samei)
                dll(dl)=length(TS(samei(dl)).paleoData_values);
            end
            
            %if they're not all thesame length, rename all tables including the length
            if length(unique(dll))>1
                pdName=['pdt' num2str(length(T.paleoData_values))];
            end
        end
        
        
        %which variables should be at the measurement table level?
        amt = {'paleoDataTableName','paleoMeasurementTableName',...
            'number','paleoNumber',...
            'paleoMeasurementTableNumber','paleoDataMD5',...
            'googleWorkSheetKey'};
        
        for am =1:length(amt)
            if any(strcmp(['paleoData_' amt{am}],fT))
                Dnew.(makeValidName(udsn{i})).paleoData.(pdName).(amt{am})=T.(['paleoData_' amt{am}]);
                pd=setdiff(pd,find(strcmp(fT,['paleoData_' amt{am}])));
            end
            
        end
        
        
        %assign in paleoData Table Name
        
        Dnew.(makeValidName(udsn{i})).paleoData.(pdName).paleoDataTableName=pdName;
        
        
        
        
        
        
        
        %get variablename name
        variableName=makeValidName(T.paleoData_variableName);
        
        %see if that name has been used already
        alreadyNames=fieldnames(Dnew.(makeValidName(udsn{i})).paleoData.(pdName));
        %iterate through numbers until it's unique
        aNi=1;
        origName=variableName;
        while any(strcmp(variableName,alreadyNames))
            variableName=[origName num2str(aNi)];
            aNi=aNi+1;
        end
        
        
        
        
        
        %add in the variable
        for pdin=1:length(pd)
            pdVarName=fT{pd(pdin)};
            
            %add in parameter
            Dnew.(makeValidName(udsn{i})).paleoData.(pdName).(variableName).(pdVarName(strfind(pdVarName,'_')+1:end))=...
                T.(fT{pd(pdin)});
            
            
        end
        
        
        if yearTS % if years are included as TS entries do something new
            
            
        else
            %add year as a column
            yearFlag=0;
            if any(strcmp('year',fT))
                if length(T.year) == length(T.paleoData_values)
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).year.values=T.year;
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).year.units='AD';
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).year.description='Year AD';
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).year.variableName='year';
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).year.dataType='float';
                    yearFlag=1;
                end
            end
            %add age as column
            ageFlag=0;
            if any(strcmp('age',fT))
                %don't add age if it's a different length than the data
                if length(T.age) == length(T.paleoData_values)
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).age.values=T.age;
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).age.units='BP';
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).age.description='Years before present (1950) BP';
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).age.variableName='age';
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).age.dataType='float';
                    ageFlag=1;
                end
            end
            %add depth as column
            depthFlag=0;
            if any(strcmp('depth',fT))
                %don't add age if it's a different length than the data
                if length(T.depth) == length(T.paleoData_values)
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).depth.values=T.depth;
                    if isfield(T,'depthUnits')
                        Dnew.(makeValidName(udsn{i})).paleoData.(pdName).depth.units=T.depthUnits;
                    end
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).depth.description='depth';
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).depth.variableName='depth';
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).depth.dataType='float';
                    depthFlag=1;
                end
            end
            if ~ageFlag && ~yearFlag && ~depthFlag
                
                error([makeValidName(udsn{i}) ': ' num2str(fts(f)) ': no age, year or depth data. The linearity (and existence) of time (or depth) are necessary assumptions in the LiPD framework | a likely problem is that the length of the data does not match the length of the year and/or age vectors'])
            end
        end
        %check for climate interpretation
        if any(strncmp('climateInterpretation_',fT,22))
            ci=find(strncmp('climateInterpretation_',fT,22));
            for cin=1:length(ci)
                ciVarName=fT{ci(cin)};
                
                %add in parameter
                Dnew.(makeValidName(udsn{i})).paleoData.(pdName).(variableName).climateInterpretation.(ciVarName(strfind(ciVarName,'_')+1:end))=...
                    T.(fT{ci(cin)});
            end
        end
        
        %check for calibration
        if any(strncmp('calibration_',fT,12))
            cai=find(strncmp('calibration_',fT,12));
            for cain=1:length(cai)
                caiVarName=fT{cai(cain)};
                
                %add in parameter
                Dnew.(makeValidName(udsn{i})).paleoData.(pdName).(variableName).calibration.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                    T.(fT{cai(cain)});
            end
        end
        
        %check for modernSystem
        if any(strncmp('modernSystem_',fT,13))
            cai=find(strncmp('modernSystem_',fT,13));
            for cain=1:length(cai)
                caiVarName=fT{cai(cain)};
                
                %add in parameter
                Dnew.(makeValidName(udsn{i})).paleoData.(pdName).(variableName).modernSystem.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                    T.(fT{cai(cain)});
            end
        end
        
        
        %check for proxySystemModel
        if any(strncmp('proxySystemModel_',fT,17))
            cai=find(strncmp('proxySystemModel_',fT,17));
            for cain=1:length(cai)
                caiVarName=fT{cai(cain)};
                
                %add in parameter
                Dnew.(makeValidName(udsn{i})).paleoData.(pdName).(variableName).proxySystemModel.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                    T.(fT{cai(cain)});
            end
        end
        
        %check for isotope interpretation
        if any(strncmp('isotopeInterpretation_',fT,22))
            iii=find(strncmp('isotopeInterpretation_',fT,22));
            for iiin=1:length(iii)
                iiiVarName=fT{iii(iiin)};
                iiname = iiiVarName(min(strfind(iiiVarName,'_'))+1:end);
                %if there's no more underscores
                if isempty(strfind(iiname,'_'))
                    %add in parameter
                    Dnew.(makeValidName(udsn{i})).paleoData.(pdName).(variableName).isotopeInterpretation.(iiname)=...
                        T.(fT{iii(iiin)});
                else %then it's an independentVariable cell.
                    if f==1
                        Dnew.(makeValidName(udsn{i})).paleoData.(pdName).(variableName).isotopeInterpretation.independentVariable=cell(1,1); %assign cell
                    end
                    iv=find(strncmp('isotopeInterpretation_independentVariable',fT,41));
                    for ivin=1:length(iv)
                        iVarName=fT{iv(ivin)};
                        ivNum=str2num(iVarName(42:(max(strfind(iVarName,'_'))-1)));
                        if isempty(ivNum)
                            ivNum=1;
                        end
                        Dnew.(makeValidName(udsn{i})).paleoData.(pdName).(variableName).isotopeInterpretation.independentVariable{ivNum}.(iVarName(max(strfind(iVarName,'_'))+1:end))=...
                            T.(fT{iv(ivin)});
                    end
                    
                    
                end
                
            end
        end
        
    end
    
    %remove empty pub cells
    Dnew.(makeValidName(udsn{i}))=removeEmptyPub(Dnew.(makeValidName(udsn{i})));
    %force convert to new structure
    if isfield(Dnew.(makeValidName(udsn{i})),'chronData')
        if isstruct(Dnew.(makeValidName(udsn{i})).chronData)
            Dnew.(makeValidName(udsn{i}))=convertLiPD1_0to1_1(Dnew.(makeValidName(udsn{i})),1);
        end
    end
    Dnew.(makeValidName(udsn{i}))=convertLiPD1_1to1_2(Dnew.(makeValidName(udsn{i})),1);
    
    
    
    
end

df=fieldnames(Dnew);
if length(df)==1
    Dnew=Dnew.(df{1});
end

delete(handle);

