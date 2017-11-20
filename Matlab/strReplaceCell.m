function cellmid = strReplaceCell(cellin,torem,torep)
%replace a subset of a cell
if ischar(torep)
   torep = {torep}; 
end

if length(torem)>1 & length(torep)==1
    %replicate it...
   torep = repmat(torep,length(torem),1); 
end

if length(torem)~=length(torep)
    error('there must be the same number of strs to remove and to replace')
end

%input is a cell full of strings, and a cell of strings to remove
cellmid = cellfun(@(x) reshape(x,1,[]),cellin,'UniformOutput',0);
for i =1:length(torem)
cellmid = cellfun(@(x) strrep(x,torem{i},torep{i}),cellmid,'UniformOutput',0);
end
