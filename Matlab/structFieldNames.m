%get a cell of structure fields within a structure
function structs=structFieldNames(P)

fields=fieldnames(P);

s=NaN;
for i=1:length(fields)
s(i)=isstruct(P.(fields{i}));
end
structs=fields(find(s));
