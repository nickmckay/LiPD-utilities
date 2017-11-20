function cellmid = strReplaceCell2(cellin,torem,torep)
%replace a whole cell of strings
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
cellmid = cellin;
for i =1:length(torem)
    index = find(strcmp(torem{i},cellin));
    if length(index)>0
       cellmid(index) = torep(i);
    end
end
