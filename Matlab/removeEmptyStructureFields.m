
function newT=removeEmptyStructureFields(T);

fnames=fieldnames(T);

for i=1:length(fnames)
   name=fnames{i};
   temp=T.(name);
   if isempty(temp) | strcmp(temp,'')  | strcmp(temp,' ')
       T=rmfield(T,name);
   end
end
newT=T;