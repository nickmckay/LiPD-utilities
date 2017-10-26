function allNan = isTableAllNan(table)


if ~isstruct(table)
    error('this should be a structure');
end


sfn = structFieldNames(table);

allNan = 1;

s=0;
while s<length(sfn) & allNan
    s=s+1;
    if isnumeric(table.(sfn{s}).values)
        if any(~isnan(table.(sfn{s}).values))
            allNan = 0;
            break
        end
    end
    
end