function outvec = forceCell2Mat(cellvec)

%convert cells with NAs to numeric matrices with NaN

outvec = nan(size(cellvec));
%replace missing value strings
mvstrings = {'NA','NaN','[]'};
for m = 1:length(mvstrings)
    mv = find(strcmpi(mvstrings{m},cellvec));
    if length(mv) == 0
        continue
    end
    
    cellvec(mv) = repmat({NaN},length(mv),1);
end
%identify remaining strings...
si = cellfun(@isstr,cellvec);
outvec(si) = cellfun(@str2num,cellvec(si));

outvec(mv) = cell2mat(cellvec(mv));
