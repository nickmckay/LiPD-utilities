function D=validateLiPD(D)

%check for year units... and tree names
fnames=fieldnames(D);

for d=1:length(fieldnames(D))
    display(fnames{d})
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
    %mtnames=fieldnames(D.(fnames{d}).paleoData);
    for p=1:length(D.(fnames{d}).paleoData)
        for pt = 1:length(D.(fnames{d}).paleoData{p}.paleoMeasurementTable)
            
            PMT  =  D.(fnames{d}).paleoData{p}.paleoMeasurementTable{pt};
            % colnames=fieldnames(D.(fnames{d}).paleoData{p}.paleoMeasurementTable{pt});
            
            
            altyearNames={'year','yearAD','yearAD','age_AD','Date','year_AD','year0x28AD0x29','year_CE','year0x28BC0x2FAD0x29'};
            altAgeNames={'age_calBP','yrBP','Age','AGE','Age_BP','Age_YBP','year0x28BP0x29'};
            altKaNames={'kyrBP'};
            
            for aY=1:length(altyearNames)
                if any(isfield(PMT,altyearNames{aY}))
                    PMT.year=PMT.(altyearNames{aY});
                    PMT=rmfield(PMT,altyearNames{aY});
                    PMT.year.units='AD';
                end
            end
            
            for aY=1:length(altAgeNames)
                if any(isfield(PMT,altAgeNames{aY}))
                    PMT.age=PMT.(altAgeNames{aY});
                    PMT=rmfield(PMT,altAgeNames{aY});
                    PMT.age.units='BP';
                    
                end
            end
            for aY=1:length(altKaNames)
                if any(isfield(PMT,altKaNames{aY}))
                    PMT.age=PMT.(altAgeNames{aY});
                    PMT.age.values = PMT.age.values*1000;
                    PMT=rmfield(PMT,altAgeNames{aY});
                    PMT.age.units='BP';
                end
            end
            
            
            if any(isfield(PMT,'year'))
                if ~isempty(strfind(PMT.year.units,'AD')) | ~isempty(strfind(PMT.year.units,'CE')) | ~isempty(strfind(PMT.year.units,'common era'))
                    PMT.year.units='AD';
                elseif ~isempty(strfind(PMT.year.units,'BP'))
                    PMT.year.units='AD';
                    PMT.year.values=1950-PMT.year.values;
                    ['converted  ' fnames{d} ' to AD']
                elseif strcmpi(PMT.year.units,'year')
                    PMT.year.units='AD';
                    ['renamed  ' fnames{d} 'units to AD']
                elseif strcmpi(PMT.year.units,'years')
                    PMT.year.units='AD';
                    ['renamed  ' fnames{d} 'units to AD']
                else
                    error([fnames{d} ': No recognized age units'])
                end
            elseif any(isfield(PMT,'age'))
                if ~isempty(strfind(PMT.age.units,'AD'))
                    if ~isfield(PMT,'year')
                        PMT.year=PMT.age;
                    end
                elseif ~isempty(strcmp(PMT.age.units,'BP'))
                    PMT.year.shortName='year';
                    PMT.year.units='AD';
                    PMT.year.values=1950-PMT.age.values;
                    ['converted  ' fnames{d} ' to AD']
                else
                    error('No recognized age units')
                end
            end
                  D.(fnames{d}).paleoData{p}.paleoMeasurementTable{pt} =   PMT;

        end
    end
    %force lower case archiveType
    D.(fnames{d}).archiveType=lower(D.(fnames{d}).archiveType);
end

%check for climate interpretation - if there is a climate interp field but
%no parameter, remove climate interp field

% for d=1:length(fnames)
%     mnames=fieldnames(D.(fnames{d}).paleoData);
%     CIflag=0;
%     for m=1:length(mnames)
%         cnames=fieldnames(D.(fnames{d}).paleoData.(mnames{m}));
%         for c=1:length(cnames)
%             if isfield(D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}),'climateInterpretation')
%                 if ~isfield(D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation,'variable')
%                     if isfield(D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation,'climateVariable')
%                         D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation.variable=D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation.climateVariable;
%                         CIflag=1;
%                         try
%                             D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation.variableDetail=D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}).climateInterpretation.climateVariableDetail;
%                         catch DO
%                         end
%                     else
%                         
%                         
%                         D.(fnames{d}).paleoData.(mnames{m}).(cnames{c})=rmfield(D.(fnames{d}).paleoData.(mnames{m}).(cnames{c}),'climateInterpretation');
%                     end
%                     
%                 else
%                     CIflag=1;
%                 end
%             end
%         end
%     end
%     dflag(d)=CIflag;
% end