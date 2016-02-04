function out=convertCellStringToNumeric(in)
%tries to gently convert a cell array to a number. If it fails, it keeps it as a
%cell.
if ~iscell(in)
    error('this only accepts cell input')
end
try %try to make it a number
    out=cell2num(in);
catch DO
    
    try
        out=cell2mat(in);
    catch DO2
        out=in;
    end
end

