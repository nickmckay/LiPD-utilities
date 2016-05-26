function L = authorCell2BibtexAuthorString(L)
%convert authors into bibTex "and" string...
if isstruct(L) %this is the whole LiPD object
    if ~isfield(L,'pub')
        error('This LiPD file doesnt have a pub section')
    end
    
    nPub = length(L.pub);
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
elseif iscell(L)
    
    if isstruct(L{1}) %then it's the whole pub object
        nPub = length(L);
        for pa = 1:nPub
            if isfield(L{pa},'author')
                if iscell(L{pa}.author)
                    las = cell2str(L{pa}.author);
                    las1 = strrep(las,''',''',' and ');
                    las2 = strrep(las1,'''','');
                    las3 = strrep(las2,'{','');
                    las4 = strrep(las3,'}','');
                    L{pa}.author=las4;
                    
                end
            end
        end
        
    else %then it's just the author cell
        
        if length(L)>1
        las = cell2str(L);
        las1 = strrep(las,''',''',' and ');
        las2 = strrep(las1,'''','');
        las3 = strrep(las2,'{','');
        las4 = strrep(las3,'}','');
        L=las4;
        else
            L=L{1};
        end
        
        
        
    end
end
