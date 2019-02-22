function TS = mergeTSfields(TS,keep,remove)


%take entries in "remove", and copy them into empty fields in "keep", then
%delete "remove"

k={TS.(keep)}';
r={TS.(remove)}';

%copy remove into empty keeps
ke=find(cellfun(@isempty,k) & ~cellfun(@isempty,r));
k(ke)=r(ke);
[TS.(keep)] = k{:};

%optionally appended removes into non empty keeps
if append
    ka=find(~cellfun(@isempty,k) & ~cellfun(@isempty,r));
    if length(ka) > 0

    end
end

TS = rmfield(TS,remove);