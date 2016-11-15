function cellmid = strRemoveCell(cellin,torem)
%input is a cell full of strings, and a cell of strings to remove
cellmid = cellfun(@(x) reshape(x,1,[]),cellin,'UniformOutput',0);
for i =1:length(torem)
cellmid = cellfun(@(x) strrep(x,torem{i},''),cellmid,'UniformOutput',0);
end
