function L = BibtexAuthorString2Cell(L)
%convert authors into bibTex "and" string...
if ~isfield(L,'pub')
   error('This LiPD file doesnt have a pub section') 
end

nPub = length(L.pub);
for pa = 1:nPub
    if isfield(L.pub{pa},'author')
        if isstr(L.pub{pa}.author)
             L.pub{pa}.author = strsplit(L.pub{pa}.author,' and ');          
        end
    end
end
