function ind=needleHaystackCell(needle,haystack)
%both needle and haystack need to be cells, although not allstrings.
%find a bunch of needles in a haystack, for cells
needle(~cellfun(@ischar,needle))={'lkasjdlkasjdklahglkahsdlkahsf'};
haystack(~cellfun(@ischar,haystack))={'NaN'};
[log,ind] = ismember(needle,haystack);
