function L = removeDuplicatePublications(L)

%remove duplicate publications


%pull out pubs
P = L.pub;


%to keep
tokeep = ones(length(P),1);
if length(P)>1
    %compare them
    for p1 = 1:(length(P)-1)
        for p2 = (p1+1):length(P)
            [m,d1,d2] = comp_struct(P{p1},P{p2});
            if ~isstruct(d2) & ~isstruct(d1)%then there are no differences in p2
%                 display(['pub ' num2str(p1) ' and  ' num2str(p2) ' are identical'])
%                 display(['removing pub ' num2str(p2)])
                tokeep(p2) = 0;
            end
        end
    end
    



if sum(tokeep)<1
    error('Something went wrong, trying to remove all publications')
end



L.pub =  P(find(tokeep));
end
end