function L = authorCell2BibtexAuthorString(L)
%convert authors into bibTex "and" string...
if ~isfield(L,'pub')
   error('This LiPD file doesnt have a pub section') 
end

nPub = length(L.pub)
for pa = 1:nPub
    if isfield(L.pub{pa},'author')
        if iscell(L.pub{pa}.author)
            las = cell2str(L.pub{pa}.author);
            las1 = strrep(las,''',''',' and ');
            las2 = strrep(las1,'''','');
            las3 = strrep(las2,'{','');
            las4 = strrep(las3,'}','');
            L.pub{pa}.author=las4;
            
        end
    end
end
