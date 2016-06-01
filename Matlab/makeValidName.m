function [newName] = makeValidName(name, protected)



if verLessThan('matlab','R2014a')
    if nargin<2
        newName = genvarname(name);
    else
        newName = genvarname(name,protected);
    end
else
    newName = matlab.lang.makeValidName(name);
end
