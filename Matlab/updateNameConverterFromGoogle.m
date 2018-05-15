%load in preferences
load LiPDUtilitiesPreferences.mat
%update TS from google sheets
sheetKeys={'1hIGLX0Q46YWtSXdpA3B2jltkAxUkWO9m2ayLad12zMs'; %variableName
    '1PtN2v523SlrnGfvWGGt7TQhkxvAYkh2qFi2EC2hNVwQ'; %units
    '1q1QSmyft8RotwEh3B0fsfJYvhwGkUX1N4wkEfYJ3pik'; %climate interp direction
    '13V30TIkPU1oftVArcKteYl93nrjgvexyN4wBSV37mS0'; %seasonality
    '1yL6KuMUXEx5bisnPn0aVp-t1tsLcAXYZDIrUM55U9Hs'; %archiveType
    '1_OvlR02LmEUJOLOaFWFaWKhr2ZOEVjUyUdeiWVmpaAc'; %proxy
        '1tH2b07E9IaNdH1LS5PvsoAZbKCQMHtc94b9z3re9eV8'; %proxyObservationType
    '1DBX5KnAdsV0I-el0NaoISW46RwlQjEQbP2QgA3Y9Zwk'; %inferredVariableType
    };

sheets={'paleoData_variableName';
    'paleoData_units';
    'climateInterpretation_interpDirection';
    'climateInterpretation_seasonality';
    'archiveType';
    'paleoData_proxy';
    'paleoData_proxyObservationType';
    'paleoData_inferredVariableType'};

if length(sheetKeys) ~= length(sheets)
    error('sheetKeys needs to match sheets')
end

for i=1:length(sheetKeys)
    %download data
    [goog]= GetGoogleSpreadsheet(sheetKeys{i});
    acceptedNames=goog(2:end,1);
    
    nameCon.(sheets{i})=cell(1,1);
    for j=1:length(acceptedNames)
        nameCon.(sheets{i}){j}.acceptedName= acceptedNames{j};
        nameCon.(sheets{i}){j}.alternates=goog(j+1,~cellfun(@isempty,goog(j+1,:)));
    end
end
lastUpdated = now;
cd(githubPath)
save nameCon.mat nameCon lastUpdated




