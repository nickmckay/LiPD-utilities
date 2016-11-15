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
    else
        error('variableName is missing from one or more columns')
    end
    
    I.(newname)=I.columns{j};
end
I=rmfield(I,'columns');


