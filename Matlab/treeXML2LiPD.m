function L = parseTreeXML(toParse,pathToFiles)

%run toby's parseTreeXML
if nargin == 1
    out = parseTreeXML(toParse);
elseif nargin ==0
    parseTreeXML()
else
    out = parseTreeXML(toParse,pathToFiles);
end

outnames = structFieldNames(out);


if length(outnames)>1
    warning('This presently only translates the first object that came from parseTreeXML')
end

X = out.(outnames{1});

%Now translate to LiPD


%get ITRDB translators
if exist('itrdbCodes.mat','file')>0
    load itrdbCodes.mat
else
    
    load LiPDUtilitiesPreferences.mat
    itrdbCodes = GetGoogleSpreadsheet('1mlvyEbwt9Xb8s_NFvKaZZ-RPgGzjX-nT6ZoLhBsaRSw');
    %remove header
    itrdbCodesGood = itrdbCodes(2:end,:);
    
    thisDir = cd;
    cd(githubPath)
    save('itrdbCodes.mat','itrdbCodesGood')
    cd(thisDir)
end

%initialize LiPD file
L.dataSetName = makeValidName(X.Name);

%handle geography
L.geo.latitude = X.lat;
L.geo.longitude = X.lon;
L.geo.elevation = X.elev;

%make empty pub
L.pub = cell(1,1);

%start PaleoData
L.paleoData{1}.paleoMeasurementTable=cell(1,1);

sfields = structFieldNames(X);

pn=1;
%Handle measurement tables
for s = 1:length(sfields)
    this = sfields{s};
    lastChar = this(end);
    %match lastChar to table
    if regexp(lastChar,'\d')==1
        %then its TRW
        lastChar = 'NULL';
    end
    
    whichRow = find(strcmpi(lastChar,itrdbCodesGood(:,1,1)));
    if length(whichRow)~=1
        error(['Dont recognize code: ' lastChar])
    end
    
    measName = itrdbCodesGood{whichRow,2};
    measUnits = itrdbCodesGood{whichRow,3};
    measDesc = itrdbCodesGood{whichRow,4};
    measPOT = itrdbCodesGood{whichRow,5};
    
    
    if isfield(X.(this),'measurements')
        
        clear MT
        %pull from ID
        
        %Table to measurementTable
        
        %measurements first (raw ring widths)
        M=X.(this).measurements;
        %year
        MT.year.values = M.Time;
        MT.year.units = 'AD';
        MT.year.variableName = 'year';
        MT.year.variableType = 'inferred';

        
        
        %now measurements
        for i = 1:length(M.ID)
            thisName = [measName '_' M.ID{i}];
            MT.(thisName).variableName = thisName;
            MT.(thisName).proxyObservationType = measName;
            MT.(thisName).units = measUnits;
            MT.(thisName).description = measDesc;
            MT.(thisName).proxyObservationType = measPOT;
            MT.(thisName).variableType = 'measured';

            MT.(thisName).values = M.Data(:,i);
        end
        MT.WDSPaleoUrl = [M.url];
        MT.paleoMeasurementTableName = this;
        MT.archiveType = 'tree';
        %assign into L
        L.paleoData{pn}.paleoMeasurementTable{1}= MT;
        L.paleoData{pn}.paleoName = measName;
    end
    
    
    if isfield(X.(this),'chronology')
        clear ST
        %put chronology in a model summary table
        C = X.(this).chronology;
        %chronology.
        %make sure same time axis
        %year
        ST.year.values = M.Time;
        ST.year.units = 'AD';
        ST.year.variableName = 'year';
        chronName = [measName '_chronology'];
        ST.(chronName).values = C.Data;
        ST.(chronName).variableName = chronName;
        ST.(chronName).variableType = 'inferred';

        ST.(chronName).units = 'unitless';
        ST.(chronName).proxyObservationType = measName;
        ST.WDSPaleoUrl = [C.url];
        
        %assign into L
        if strcmp(lastChar,'a') | strcmp(lastChar,'r')
            if isfield(L,'paleoData')
            %then add it as a model on TRW
            if strcmp(L.paleoData{1}.paleoName,'totalRingWidth')
                %how many models?
                if isfield(L.paleoData{1},'paleoModel')
                    wm = length(L.paleoData{1}.paleoModel)+1;
                else
                    wm = 1;
                end
                L.paleoData{1}.paleoModel{wm}.summaryTable= ST;
            else
                L.paleoData{pn}.paleoModel{1}.summaryTable= ST;
                L.paleoData{pn}.paleoName = measName;
                pn=pn+1;
            end
            else
                L.paleoData{pn}.paleoModel{1}.summaryTable= ST;
                L.paleoData{pn}.paleoName = measName;
                pn=pn+1;               
            end
        else
            L.paleoData{pn}.paleoModel{1}.summaryTable= ST;
                L.paleoData{pn}.paleoName = measName;
                pn=pn+1;        
            
        end
        
        
    else
        pn=pn+1;
    end
    
    
end

end








