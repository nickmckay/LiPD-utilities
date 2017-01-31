function str= removeCarriageReturn( str )


if ischar(str)
    
    str = regexprep(str,'\r\n|\n|\r',' ');
    
end

