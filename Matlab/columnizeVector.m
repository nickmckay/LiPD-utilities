function V = columnizeVector(V)
if min(size(V))>1
    display(V)
    error('this is not a vector')
end
if size(V,1)==1
    V=V';
end


end