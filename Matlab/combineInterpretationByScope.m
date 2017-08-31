%combine interpretation by scope

mts = TS(1);
fnames = fieldnames(mts);
scopes = {'climate','isotope','ecology'};

for s = 1:length(scopes)
   ts = [scopes{s} 'Interpretation'];
   
   %how many scopes with this interpretation?
        mts = TS(i);
        ss = [ ts '[0-9]'];
    intnumcell = uniqueCell(cellfun(@(x) x(regexp(x,ss,'end')), fnames,'UniformOutput',0));
          nInterp = max(cellfun(@str2num, intnumcell(2:end))); 
    
    
    
end