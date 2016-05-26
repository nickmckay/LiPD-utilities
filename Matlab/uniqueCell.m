function u=uniqueCell(X)
%returns unique string entries in a cell ignoring, empties and non-strings
g=find(cellfun(@ischar,X));
u=unique(X(g));


