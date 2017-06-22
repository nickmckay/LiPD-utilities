function L = arstan2LiPD(siteName,arstanDir,L,pd,wm)

origDir = cd;


if nargin<2
    arstanDir = uigetdir('Select the directory that contains the ARSTAN output files')
end
cd(arstanDir)

%get ITRDB translators
if exist('itrdbCodes.mat','file')>0
    load itrdbCodes.mat
else
    itrdbCodes = GetGoogleSpreadsheet('1mlvyEbwt9Xb8s_NFvKaZZ-RPgGzjX-nT6ZoLhBsaRSw');
    %remove header
    itrdbCodesGood = itrdbCodes(2:end,:);
    
    thisDir = cd;
    cd(githubPath)
    save('itrdbCodes.mat','itrdbCodesGood')
    cd(thisDir)
end
%


this = siteName;
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


%find all the tab files
alltab=dir([siteName '*tabs.txt']);
allRbar=dir([siteName '*res_rbar.txt']);
allLog=dir([siteName '*_log.txt']);










if nargin < 3
    %create new LiPD file and add stuff in...
    L.dataSetName = siteName;
    L.geo.latitude = NaN;
    L.geo.longitude = NaN;
    L.geo.elevation = NaN;
    L.pub = cell(1,1);
    L.paleoData = cell(1,1);
end

if nargin < 4
    %which paleodata?
    if length(L.paleoData) ==1
    pd = 1;
    else
        for pp =1:length(L.paleoData)
            if isfield(L.paleoData{pp},'paleoName')
                display([num2str(pp) ' - ' L.paleoData{pp}.paleoName]);
            else
                display([num2str(pp) ' - unnamed'])
            end           
        end
        pd = input('Which paleoData do you want to add this chronology to?');       
    end
end

if nargin <5
    wm = 1; %start with 1, change if needed
    if isfield(L,'paleoData')
        if isfield(L.paleoData{pd},'paleoModel')
            wm = length(L.paleoData{pd}.paleoModel) + 1 ; %create a new model by default
        end
    end
end



for i=1:length(alltab)
    tabnames{i,1}=alltab(i).name;
    rbarnames{i,1}=allRbar(i).name;
    lognames{i,1}= allLog(i).name;
    %assign in name
    
    
    tabdata=dlmread(tabnames{i,1},'\t',1,0);
    
    rbarData=dlmread(rbarnames{i,1},'\t',1,0);
    
    %write measurement table
    
    MT.archiveType='tree';
    
    
    %assign measurements
    %year
    MT.year.values=tabdata(:,1);
    MT.year.units='AD';
    MT.variableName='year';
    MT.variableType = 'inferred';
    
    %sampleDensity
    sName='sampleDensity';
    MT.(sName).variableName=sName;
    MT.(sName).values=tabdata(:,2);
    MT.(sName).units='number of samples';
    MT.variableType = 'measured';
    
    %segment
    sName='segment';
    MT.(sName).variableName=sName;
    MT.(sName).values=tabdata(:,3);
    MT.(sName).units='NA';
    MT.variableType = 'inferred';
    
    
    %rawRingWidth
    sName=measName;
    MT.(sName).variableName=sName;
    MT.(sName).values=tabdata(:,5);
    MT.(sName).units='unitless';
    MT.variableType = 'inferred';
    
    
    %standardized Index
    sName=[measName '_chronology'];
    MT.(sName).variableName=sName;
    MT.(sName).values=tabdata(:,6);
    MT.(sName).units='unitless';
    MT.variableType = 'inferred';
    MT.inferredVariableType = measName;
    
    %residual
    sName='residual';
    MT.(sName).variableName=sName;
    MT.(sName).values=tabdata(:,7);
    MT.(sName).units='unitless';
    MT.variableType = 'inferred';
    
    %ars
    sName='ARS';
    MT.(sName).variableName=sName;
    MT.(sName).values=tabdata(:,8);
    MT.(sName).units='unitless';
    MT.variableType = 'inferred';
    
    
    
    %assign in rbar
    % assign rbar and EPS to nearest year + repeat
    sNamesRbar={'corrs','rbar','sdev','serr','eps','cores'};
    RbarUnits={'unitless','unitless','unitless','unitless','unitless','unitless'};
    for ss=1:length(sNamesRbar)
        MT.(sNamesRbar{ss}).variableName=sNamesRbar{ss};
        MT.(sNamesRbar{ss}).units=RbarUnits{ss};
        for yy=1:length(tabdata(:,1))
            nearesti=find_nearest(tabdata(yy,1),rbarData(:,1));
            MT.(sNamesRbar{ss}).values(yy,1)=rbarData(nearesti,ss+1);
        end
    end
    
    
    %add in method info
    
    %%% Read ARSTAN .rwl_log.txt file output variables
    
    [method.missData] = textread(lognames{i,1},'%d %*[^\n]', 1,'headerlines',2);
    [method.transform] = textread(lognames{i,1},'%d %*[^\n]', 1,'headerlines',3);
    [d1a, d1b] = textread(lognames{i,1},'%d %d %*[^\n]', 1,'headerlines',4);
    [d2a, d2b] = textread(lognames{i,1},'%d %d %*[^\n]', 1,'headerlines',5);
    [method.robustDetrend] = textread(lognames{i,1},'%d %*[^\n]', 1,'headerlines',6);
    [method.idxCalc]= textread(lognames{i,1},'%d %*[^\n]', 1,'headerlines',8);
    [ar1, ar2]= textread(lognames{i,1},'%d %d %*[^\n]', 1,'headerlines',9);
    [method.poolArOrder]= textread(lognames{i,1},'%d %*[^\n]', 1,'headerlines',10);
    [method.seriesArOrder]= textread(lognames{i,1},'%d %*[^\n]', 1,'headerlines',11);
    [m1, m2, m3]= textread(lognames{i,1},'%d %d %d %*[^\n]', 1,'headerlines',12);
    [method.varStabilize] = textread(lognames{i,1},'%d %*[^\n]', 1,'headerlines',13);
    [cY1, cY2] = textread(lognames{i,1},'%d %d %*[^\n]', 1,'headerlines',14);
    [rb1, rb2] = textread(lognames{i,1},'%d %d %*[^\n]', 1,'headerlines',16);
    [method.detrend1] = [d1a; d1b]; clear d1a d1b
    [method.detrend2] = [d2a; d2b]; clear d2a d2b
    [method.arMethod] = [ar1; ar2]; clear ar1 ar2
    [method.chronMethod] = [m1; m2; m3]; clear m1 m2 m3
    [method.commonYrs] = [cY1; cY2]; clear cY1 cY2
    [method.rbarWindow] = [rb1; rb2]; clear rb1 rb2
    
    %%% Variables
    %  Consult program ARSTAN for numerical code meanings
    
    %  missing data in gap     = 'missData'
    %  data transformation     = 'transform'
    %  first detrending        = 'detrend1'
    %  second detrending       = 'detrend2'
    %  robust detrending       = 'robustDetrend'
    %  index calculation       = 'idxCalc'
    %  ar modeling method      = 'arMethod'
    %  pooled ar order         = 'poolArOrder'
    %  series ar order         = 'seriesArOrder'
    %  mean chronology         = 'chronMethod'
    %  stabilize variance      = 'varStabilize'
    %  common period years     = 'commonYrs'
    
    
    %translate Detrending method code into english:
    transTable = {-6	'ageDepSpline';
        -5	'friedmanSmooth';
        -4	'lowessSmooth';
        -3	'medianFilter';
        -2	'rcs';
        -1	'firstDifference';
        0	'none';
        1	'negExOrLinearRegAnySlope';
        2	'negExOrLinearRegNegSlope';
        3	'negExAnyK';
        4	'linearRegAnySlope';
        5	'linearRegNegativeSlope';
        6	'horizontal';
        7	'hugershoff';
        8	'negExGeneral'};
    
    if isnumeric(method.detrend1(1))
        if method.detrend1(1) > 9
            MT.detrendingMethod = 'fixedNSmooth';
        elseif  method.detrend1(1) <= -9
            MT.detrendingMethod = 'pctSmooth';
        else
            
            codeMatch1 = find(method.detrend1(1) == cell2mat(transTable(:,1)));
            
            if ~isempty(codeMatch1)
                MT.detrendingMethod = transTable{codeMatch1,2};
            else
                MT.detrendingMethod = 'unknown';
                warning('couldnt match detrending method to known name');
            end
        end
    end
        
    if isnumeric(method.detrend2(1))
        if method.detrend2(1) > 9
            MT.detrendingMethod2 = 'fixedNSmooth';
        elseif  method.detrend2(1) <= -9
            MT.detrendingMethod2 = 'pctSmooth';
        else
            
            codeMatch2 = find(method.detrend2(1) == cell2mat(transTable(:,1)));
            
            if ~isempty(codeMatch2)
                MT.detrendingMethod2 = transTable{codeMatch2,2};
            else
                MT.detrendingMethod2 = 'unknown';
                warning('couldnt match detrending method to known name');
            end
        end
    end
        
        
        
        L.paleoData{pd}.paleoModel{wm}.method=method;
       
        MT.summaryTableName = [siteName '_' MT.detrendingMethod];
        
        
        L.paleoData{pd}.paleoModel{wm}.summaryTable = MT;
        
    end
    
    
end

