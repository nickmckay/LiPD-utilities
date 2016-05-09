function TS = authorCell2BibtexAuthorStringTS(TS)
%convert authors into bibTex "and" string...
fnames = fieldnames(TS);
auth=find(~cellfun(@isempty,(strfind(fnames,'author'))));
if isempty(auth)
   error('This TS file doesnt have a pub section') 
end

for a = 1:length(auth)
    pubStruct = {TS.(fnames{auth(a)})}';
nPub = length(pubStruct);
for pa = 1:nPub
        if iscell(pubStruct{pa})
            las = cell2str(pubStruct{pa});
            las1 = strrep(las,''',''',' and ');
            las2 = strrep(las1,'''','');
            las3 = strrep(las2,'{','');
            las4 = strrep(las3,'}','');
            pubStruct{pa}=las4;
            
        end
end
[TS.(fnames{auth(a)})] = pubStruct{:};

end