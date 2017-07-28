function I = processLiPDColumns(I)
%turns columns of structures into named structures, then removes columns


if ~isfield(I,'columns')
    error('No field called columns')
end

for j=1:length(I.columns)
    if isfield(I.columns{j},'variableName')
        newname=genvarname(I.columns{j}.variableName,fieldnames(I));
    elseif isfield(I.columns{j},'parameter')
        newname=genvarname(I.columns{j}.parameter,fieldnames(I));%included for older versions
        warning('use of the term "parameter" is deprecated, and has been replaced with "variableName"')
    elseif isfield(I.columns{j},'shortname')
        newname=genvarname(I.columns{j}.shortname,fieldnames(I));%included for older versions
        warning('use of the term "shortname" is very deprecated, and has been replaced with "variableName"')
    else
        error('variableName is missing from one or more columns')
    end
    
    
    I.(newname)=I.columns{j};
    
    %try to make cells, not cells
    
    
    
    %calculate summary statistics on columns
    values = I.(newname).values;
    
    %replace missing values
    if isfield(I.(newname),'missingValue')
        torep = find(strcmp(I.(newname).missingValue,values));
        if length(torep)>0
            if ~iscell(values)
                values(torep)   = nan(length(torep),1);
            else
                values(torep)   = repmat({NaN},length(torep),1);
            end
        end
    end
    
    %also replace NaN and NA
    torep = find(strcmpi('NaN',values) | strcmp('NA',values));
    if length(torep)>0
        if ~iscell(values)
            values(torep)   = nan(length(torep),1);
        else
            values(torep)   = repmat({NaN},length(torep),1);
        end
    end
    
    
    I.(newname).missingValue = 'NaN';
    
    if ~iscell(values)
        I.(newname).hasMaxValue = nanmax(values);
        I.(newname).hasMinValue = nanmin(values);
        I.(newname).hasMeanValue = nanmean(values);
        I.(newname).hasMedianValue = nanmedian(values);
        
    else
        
    end
    
    
    I.(newname).values = values;
    
    
    
    
    
end
I=rmfield(I,'columns');


