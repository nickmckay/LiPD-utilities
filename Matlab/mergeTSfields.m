function TS = mergeTSfields(TS,keep,remove)


%take entries in "remove", and copy them into empty fields in "keep", then
%delete "remove"

k={TS.(keep)}';
r={TS.(remove)}';

ke=find(cellfun(@isempty,k) & ~cellfun(@isempty,r));
k(ke)=r(ke);
[TS.(keep)] = k{:};
TS = rmfield(TS,remove);