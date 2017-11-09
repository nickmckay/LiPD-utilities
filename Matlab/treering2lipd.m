function L = treering2lipd(toParse,varargin)

if nargin<1
    answer = input('Do you want to load a NOAA XML file (''x'') or a directory of rwl and/or crn files (''d'')?)');
    if strncmpi(answer,'d',1)
        toParse = uigetdir;
    else
        [filepath, dirpath] = uigetfile('.xml');
        toParse = [dirpath filepath];
    end
end


%split apart information
%if nargin <=1
[pathstr, fname, ext] = fileparts(toParse);
%end


if strcmpi(ext,'.xml')
    
    %run toby's parseTreeXML
    if nargin <=1
        out = parseTreeXML(toParse);
    else
        out = parseTreeXML(toParse,pathToFiles);
    end
    
elseif isempty(ext)
    if nargin>2
        % out = readRwlCrn(toParse,strjoin(varargin,','));
        out = readRwlCrn(toParse,varargin{:});
    else
        out = readRwlCrn(toParse);
    end
    
else
    error('Only accepts .xml files and directories at present')
    
    
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
try
    L.geo.elevation = X.elev;
catch DO
end
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
        try
            MT.WDSPaleoUrl = [M.url];
        catch DO
        end
        
        MT.paleoMeasurementTableName = this;
        MT.archiveType = 'tree';
        %assign into L
        L.paleoData{pn}.paleoMeasurementTable{1}= MT;
        L.paleoData{pn}.paleoName = measName;
        %        pn=pn+1;
    end
    
    
    if isfield(X.(this),'chronology')
        C = X.(this).chronology;
        clear ST
        for ncrn = 1:length(C.crnCell)%loop through chronologies
            
            %put chronology in a model summary table
            %chronology.
            %make sure same time axis
            %year
            
            thisCrn = C.crnCell{ncrn};
            
            ST.year.values = thisCrn.yr;
            ST.year.units = 'AD';
            ST.year.variableName = 'year';
            
            chronTableName = [measName '_chronology'];
            
            if isfield(thisCrn,'chronType')
                chronName = [thisCrn.chronType];
                ST.(chronName).chronType = chronName;
            else
                chronName=makeUniqueStrings(chronTableName,structFieldNames(ST));
            end
            
            ST.(chronName).values = thisCrn.x;
            ST.(chronName).variableName = chronName;
            ST.(chronName).variableType = 'inferred';
            ST.(chronName).units = 'unitless';
            ST.(chronName).proxyObservationType = measName;
            
            
            try
                ST.WDSPaleoUrl = [C.url];
            catch DO
            end
            
            %add ncores if it's the first one
            if ncrn==1
                ST.nCores.values = thisCrn.s;
                ST.nCores.units = 'count';
                ST.nCores.variableName = 'nCores';
                ST.nCores.description = 'Number of samples/cores used in the chronology at each year';
            end
            
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
                
            end
            
        end
    else
    end
    pn=pn+1;
    
    
end
L.lipdVersion = 1.2;

L = convertLiPD1_2to1_3(L);

end










