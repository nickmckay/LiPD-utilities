function D=updateLiPDLibraryFromGoogle(D)

dnames = fieldnames(D);
for d=1:length(dnames)
    try
   D.(dnames{d}) = updateLiPDfromGoogle(D.(dnames{d}));
    catch
       warning([dnames{d} ' update failed. ' D.(dnames{d}).googleSpreadSheetKey])
    end
end
