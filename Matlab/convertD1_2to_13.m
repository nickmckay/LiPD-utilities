%update to 1.3

dnames = fieldnames(D);

for d = 1:length(dnames)
   D13.(dnames{d}) = convertLiPD1_2to1_3(D.(dnames{d}));
end
