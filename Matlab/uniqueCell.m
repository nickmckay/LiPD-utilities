function [u,ia ,ib]=uniqueCell(X)
%returns unique string entries in a cell ignoring, empties and non-strings
g=find(cellfun(@ischar,X));
[u,ia,ib]=unique(X(g));
ia = g(ia);
ib = g(ib);


