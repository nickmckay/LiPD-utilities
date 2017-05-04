

dnames = fieldnames(D);

for d=1:length(dnames)
         d
    [bibout,key,D.(dnames{d})] =  pub2bib(D.(dnames{d}),1);  
   if d==1 
       allBib = bibout;
       keys = key;
   else
   allBib = [allBib ; bibout];
   keys = [keys ; key];
   end
    
    
end

good = find(~cellfun(@isempty,allBib));
allBib=allBib(good);
keys = keys(good);

[ukeys,ia,ib]=unique(keys);
good = ia;
allBib=allBib(good);
keys = keys(good);

%change @dataCitation to @misc
allBib = cellfun(@(x) strrep(x,'@dataCitation','@online'),allBib,'UniformOutput',0);

writeCell2Bib(allBib);