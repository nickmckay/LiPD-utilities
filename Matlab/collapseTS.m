%collapseTS
%converts TS (LiPD TS object) structure to D (Lipd Hierarchical Object) structure
clear
load ~/Dropbox/Pages2kPhase2/p2kDatabaseWithNewTSIDs.mat TS
%update from google
run('~/Dropbox/Pages2kPhase2/updateTSfromGoogle.m');

%update TS naming to LiPD
%remove dataSetName field for now
TS=rmfield(TS,'dataSetName');

%HACKS
TS(4504).pubYear=2005;
TS(4508).pubYear=2007;
TS(4579).pubYear=2002;
TS(4579).pub_year=2002;
TS(4646).pubYear=2011;
TS(4646).pub_year=2011;

TS=renameTS(TS,1); %removing entries that aren't in the table

%%
%create a LiPD object for every unique dataSetName
udsn=unique({TS.dataSetName}');

for i=1:length(udsn)
    %find TS entries that match that unique Name
    fts=find(strcmp(udsn{i},{TS.dataSetName}'));
    
    for f=1:length(fts) %make a paleoDataTable entry for each TS
        T=TS(fts(f));
        T=removeEmptyStructureFields(T);
        fT=fieldnames(T);
        
        %base level
        %all the fields that don't have underscores (except year and age)
        b=find(cellfun(@isempty,(strfind(fT,'_'))));
        yi=find(strcmpi('year',fT));
        ai=find(strcmpi('age',fT));
        yai=union(ai,yi);
        b=setdiff(b,yai);
        
        for bi=1:length(b)
            Dnew.(matlab.lang.makeValidName(udsn{i})).(fT{b(bi)})=T.(fT{b(bi)});
        end
        
        %funding
        fun=find(strncmp('funding_',fT,8));
        if numel(fun)>0
            Dnew.(matlab.lang.makeValidName(udsn{i})).funding=cell(1,1); %assign cell to funding
            for fin=1:length(fun)
                funVarName=fT{fun(fin)};
                fundNum=str2num(funVarName(8:(strfind(funVarName,'_')-1)));
                Dnew.(matlab.lang.makeValidName(udsn{i})).funding{fundNum}.(funVarName(strfind(funVarName,'_')+1:end))=...
                    T.(fT{fun(fin)});
            end
        end
        
        
        %pub
        if f==1
            Dnew.(matlab.lang.makeValidName(udsn{i})).pub=cell(1,1); %assign cell to pub
        end
        p=find(strncmp('pub',fT,3));
        for pin=1:length(p)
            pubVarName=fT{p(pin)};
            pubNum=str2num(pubVarName(4:(strfind(pubVarName,'_')-1)));
            Dnew.(matlab.lang.makeValidName(udsn{i})).pub{pubNum}.(pubVarName(strfind(pubVarName,'_')+1:end))=...
                T.(fT{p(pin)});
        end
        
        %geo
        if f==1
            Dnew.(matlab.lang.makeValidName(udsn{i})).geo=struct; %assign geo to structure
        end
        g=find(strncmp('geo_',fT,4));
        
        for gin=1:length(g)
            geoVarName=fT{g(gin)};
            
            Dnew.(matlab.lang.makeValidName(udsn{i})).geo.(geoVarName(strfind(geoVarName,'_')+1:end))=...
                T.(fT{g(gin)});
        end
        
        
        
        %paleoData
        if f==1
            Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData=struct; %assign paleoData to structure
        end
        pd=find(strncmp('paleoData_',fT,10));
        
        %get or create the name of the relevant paleodata table
        if isfield(T,'paleoData_tableName')
            pdName=T.paleoData_tableName;
        else
            pdName='s1';
        end
        
        %get parameter name
        paramName=matlab.lang.makeValidName(T.paleoData_parameter);
        
        for pdin=1:length(pd)
            pdVarName=fT{pd(pdin)};
            
            %add in parameter
            Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData.(pdName).(paramName).(pdVarName(strfind(pdVarName,'_')+1:end))=...
                T.(fT{pd(pdin)});
        end
        
        %add year as a column
        if any(strcmp('year',fT))
            Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData.(pdName).year.values=T.year;
            Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData.(pdName).year.units='AD';
            Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData.(pdName).year.description='Year AD';
            Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData.(pdName).year.parameter='year';
            
        end
        %add age as column
        if any(strcmp('age',fT))
            Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData.(pdName).age.values=T.age;
            Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData.(pdName).age.units='BP';
            Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData.(pdName).age.description='Years before present (1950) BP';
            Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData.(pdName).age.parameter='age';
            
        end
        
        %check for climate interpretation
        if any(strncmp('climateInterpretation_',fT,22))
            ci=find(strncmp('climateInterpretation_',fT,22));
            for cin=1:length(ci)
                ciVarName=fT{ci(cin)};
                
                %add in parameter
                Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData.(pdName).(paramName).climateInterpretation.(ciVarName(strfind(ciVarName,'_')+1:end))=...
                    T.(fT{ci(cin)});
            end
        end
        
        %check for calibration
        if any(strncmp('calibration_',fT,12))
            cai=find(strncmp('calibration_',fT,12));
            for cain=1:length(cai)
                caiVarName=fT{cai(cain)};
                
                %add in parameter
                Dnew.(matlab.lang.makeValidName(udsn{i})).paleoData.(pdName).(paramName).calibration.(caiVarName(strfind(caiVarName,'_')+1:end))=...
                    T.(fT{cai(cain)});
            end
        end
        
    end
    
end