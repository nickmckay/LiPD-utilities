function L = BibtexAuthorString2Cell(L)
%convert authors into bibTex "and" string...

if isstruct(L)%then it's a whole LiPD object
if ~isfield(L,'pub')
   error('This LiPD file doesnt have a pub section') 
end

nPub = length(L.pub);
for pa = 1:nPub
    if isfield(L.pub{pa},'author')
        if ischar(L.pub{pa}.author)
             L.pub{pa}.author = strsplit(L.pub{pa}.author,' and ');          
        end
    end
end
elseif iscell(L)%then it's a pub object
    nPub = length(L);
for pa = 1:nPub
    if isfield(L{pa},'author')
        if ischar(L{pa}.author)
             L{pa}.author = strsplit(L{pa}.author,' and ');          
        end
    end
end
    
    
elseif ischar(L)%then it's just the string
    
                 L = strsplit(L,' and ');          

    
end