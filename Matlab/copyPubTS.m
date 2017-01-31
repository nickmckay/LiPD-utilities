function TS = copyPubTS(TS,tocopy,torep,pn);
%copy pub fields in TS

tnames = fieldnames(TS);

if length(tocopy)~=1
    error('Can only copy a single pub')
end
if nargin<4
pn = 1;

end

pNames = tnames(strncmp(['pub' num2str(pn)],tnames,4));

for i=1:length(pNames)
    for j=1:length(torep)
   [TS(torep(j)).(pNames{i})] = TS(tocopy).(pNames{i});
    end
    
end