function V = columnizeVector(V)
if min(size(V))~=1
    error('this is not a vector')
end
if size(V,1)==1
    V=V';
end


end