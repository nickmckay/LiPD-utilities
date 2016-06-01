function [newName] = makeValidName(name, protected)



if verLessThan('matlab','8.3')
    if nargin<2
        newName = genvarname(name);
    else
        newName = genvarname(name,protected);
    end
else
    newName = matlab.lang.makeValidName(name);
end
