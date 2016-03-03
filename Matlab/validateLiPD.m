function D=validateLiPD(D)

%check for year units... and tree names
fnames=fieldnames(D);

for d=1:length(fieldnames(D))
    %standardize archive name
    if ~isfield(D.(fnames{d}),'archiveType')
                D.(fnames{d}).archiveType='unknown';
    end
    if strncmp('tree',lower(D.(fnames{d}).archiveType),4)
        D.(fnames{d}).archiveType='tree';
    elseif strncmp('lake',lower(D.(fnames{d}).archiveType),4) | strncmp('paleolimnology',lower(D.(fnames{d}).archiveType),14)
        D.(fnames{d}).archiveType='lake sediment';
    end
    %standardize year
    mtnames=fieldnames(D.(fnames{d}).paleoData);
    for mt=1:length(mtnames)
        colnames=fieldnames(D.(fnames{d}).paleoData.(mtnames{mt}));
               
        
        altYearNames={'year','YearAD','yearAD','age_AD','Date','year_AD','Year0x28AD0x29','Year_CE','Year0x28BC0x2FAD0x29'};
        altAgeNames={'age_calBP','yrBP','Age','AGE','Age_BP','Age_YBP','Year0x28BP0x29'};
        altKaNames={'kyrBP'};
        
        for aY=1:length(altYearNames)
            if any(isfield(D.(fnames{d}).paleoData.(mtnames{mt}),altYearNames{aY}))
                D.(fnames{d}).paleoData.(mtnames{mt}).Year=D.(fnames{d}).paleoData.(mtnames{mt}).(altYearNames{aY});
                D.(fnames{d}).paleoData.(mtnames{mt})=rmfield(D.(fnames{d}).paleoData.(mtnames{mt}),altYearNames{aY});
                D.(fnames{d}).paleoData.(mtnames{mt}).Year.units='AD';
            end
        end
        
        for aY=1:length(altAgeNames)
            if any(isfield(D.(fnames{d}).paleoData.(mtnames{mt}),altAgeNames{aY}))
                D.(fnames{d}).paleoData.(mtnames{mt}).age=D.(fnames{d}).paleoData.(mtnames{mt}).(altAgeNames{aY});
                D.(fnames{d}).paleoData.(mtnames{mt})=rmfield(D.(fnames{d}).paleoData.(mtnames{mt}),altAgeNames{aY});
                D.(fnames{d}).paleoData.(mtnames{mt}).age.units='BP';
            end
        end
        for aY=1:length(altKaNames)
            if any(isfield(D.(fnames{d}).paleoData.(mtnames{mt}),altKaNames{aY}))
                D.(fnames{d}).paleoData.(mtnames{mt}).age=D.(fnames{d}).paleoData.(mtnames{mt}).(altKaNames{aY});
                D.(fnames{d}).paleoData.(mtnames{mt}).age.values= D.(fnames{d}).paleoData.(mtnames{mt}).age.values.*1000;
                
                D.(fnames{d}).paleoData.(mtnames{mt})=rmfield(D.(fnames{d}).paleoData.(mtnames{mt}),altKaNames{aY});
                D.(fnames{d}).paleoData.(mtnames{mt}).age.units='BP';
            end
        end
        
        
        if any(isfield(D.(fnames{d}).paleoData.(mtnames{mt}),'Year'))
            if ~isempty(strfind(D.(fnames{d}).paleoData.(mtnames{mt}).Year.units,'AD')) | ~isempty(strfind(D.(fnames{d}).paleoData.(mtnames{mt}).Year.units,'CE')) | ~isempty(strfind(D.(fnames{d}).paleoData.(mtnames{mt}).Year.units,'common era'))
                D.(fnames{d}).paleoData.(mtnames{mt}).Year.units='AD';
            elseif ~isempty(strfind(D.(fnames{d}).paleoData.(mtnames{mt}).Year.units,'BP'))
                D.(fnames{d}).paleoData.(mtnames{mt}).Year.units='AD';
                D.(fnames{d}).paleoData.(mtnames{mt}).Year.values=1950-D.(fnames{d}).paleoData.(mtnames{mt}).Year.values;
                ['converted  ' fnames{d} ' to AD']
            elseif strcmpi(D.(fnames{d}).paleoData.(mtnames{mt}).Year.units,'year')
                D.(fnames{d}).paleoData.(mtnames{mt}).Year.units='AD';
                ['renamed  ' fnames{d} 'units to AD']
            elseif strcmpi(D.(fnames{d}).paleoData.(mtnames{mt}).Year.units,'years')
                D.(fnames{d}).paleoData.(mtnames{mt}).Year.units='AD';
                ['renamed  ' fnames{d} 'units to AD']
            else
                error([fnames{d} ': No recognized age units'])
            end
        elseif any(isfield(D.(fnames{d}).paleoData.(mtnames{mt}),'age'))
            if ~isempty(strfind(D.(fnames{d}).paleoData.(mtnames{mt}).age.units,'AD'))
                if ~isfield(D.(fnames{d}).paleoData.(mtnames{mt}),'Year')
                    D.(fnames{d}).paleoData.(mtnames{mt}).Year=D.(fnames{d}).paleoData.(mtnames{mt}).age;
                end
            elseif ~isempty(strcmp(D.(fnames{d}).paleoData.(mtnames{mt}).age.units,'BP'))
                D.(fnames{d}).paleoData.(mtnames{mt}).Year.shortName='Year';
                D.(fnames{d}).paleoData.(mtnames{mt}).Year.units='AD';
                D.(fnames{d}).paleoData.(mtnames{mt}).Year.values=1950-D.(fnames{d}).paleoData.(mtnames{mt}).age.values;
                ['converted  ' fnames{d} ' to AD']
            else
                error('No recognized age units')
            end
        end
    end
    %force lower case archiveType
    D.(fnames{d}).archiveType=lower(D.(fnames{d}).archiveType);
end

%check for climate interpretation - if there is a climate interp field but
%no parameter, remove climate interp field

for d=1:length(fnames)
    mnames=fieldnames(D.(fnames{d}).paleoData);
    CIflag=0;
    for m=1:length(mnames)
        cnames=fieldnames(D.(fnames{d}).paleoData.(mnames{m}));
        for c=1:length(cnames)
            if isfield(D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}),'climateInterpretation')
                if ~isfield(D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation,'variable')
                    if isfield(D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation,'climateVariable')
                        D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation.variable=D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation.climateVariable;
                        CIflag=1;
                        try
                            D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation.variableDetail=D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation.climateVariableDetail;
                        catch DO
                        end
                    else
                        
                        
                        D.(fnames{d}).paleoData.(mnames{m}).(cnames{c})=rmfield(D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}),'climateInterpretation');
                    end
                    
                else
                    CIflag=1;
                end
            end
        end
    end
    dflag(d)=CIflag;
end