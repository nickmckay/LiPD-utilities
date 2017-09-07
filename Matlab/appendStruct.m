function S = appendStruct(S1,S2)

%force them to have the same fieldnames by adding in empties
f1 = fieldnames(S1);
f2 = fieldnames(S2);

f2missing = setdiff(f1,f2);
f1missing = setdiff(f2,f1);

bc1 = cell(length(S1),1);
for f = 1:length(f1missing)
   [S1.(f1missing{f})] = bc1{:}; 
end
S1 = structord(S1);

bc2 = cell(length(S2),1);
for f = 1:length(f2missing)
   [S2.(f2missing{f})] = bc2{:}; 
end

S2 = structord(S2);

S = [S1 S2];




