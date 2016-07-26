function D=standardizeLiPDLibrary(D)

dnames = fieldnames(D);
for d=1:length(dnames)
   D.(dnames{d}) = standardizeLiPD(D.(dnames{d})); 
    
end