function I = processLiPDColumns(I)
%turns columns of structures into named structures, then removes columns


if ~isfield(I,'columns')
    error('No field called columns')
end

for j=1:length(I.columns)
    newname=genvarname(I.columns{j}.variableName,fieldnames(I));
    I.(newname)=I.columns{j};
end
I=rmfield(I,'columns');


