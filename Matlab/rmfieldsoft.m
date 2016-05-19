function D=rmfieldsoft(D,torem)
%removes fields from a structure if they're there, does nothing if they're
%absent
if ischar(torem)
    torem={torem};
end

if iscell(torem)
    for i=1:length(torem)
        if isfield(D,torem{i})
            D=rmfield(D,torem{i});
        end
    end
else
    error('second input must be a string or a cell')
    
end


