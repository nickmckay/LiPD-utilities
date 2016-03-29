function matout=cell2num(cellin)
matout=nan(size(cellin,1),size(cellin,2));
for i=1:size(cellin,1)
    for j=1:size(cellin,2)
       % [i j]
   matout(i,j)=str2num(cellin{i,j}); 
    end
end
