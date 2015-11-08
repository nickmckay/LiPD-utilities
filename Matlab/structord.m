function bar = structord(foo)
% Sort structure fieldnames alphabetically

Dimensions = size(foo); 
foo = foo(:);
[f,ix] = sort(fieldnames(foo));
v = struct2cell(foo);
bar = cell2struct(v(ix,:),f,1); 
bar = reshape(bar,Dimensions);