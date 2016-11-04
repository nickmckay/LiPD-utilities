function L=removeEmptyPub(L)
L.pub=L.pub(~cellfun(@isempty,L.pub));
