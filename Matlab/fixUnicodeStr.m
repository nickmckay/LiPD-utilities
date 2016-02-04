function x=fixUnicodeStr(x)
%fix unicode in strings

if ischar(x)
 
    %first check for double slashes
start=strfind(x,'\\u');

if ~isempty(start)
    
    for i =length(start):-1:1
        u=x(start(i)+3:start(i)+6);
        x(start(i))=char(hex2dec(u));
        x(start(i)+1:start(i)+6)='';
        
    end
end    
    %then check for singles
    
    
start=strfind(x,'\u');

if ~isempty(start)
    
    for i =length(start):-1:1
        u=x(start(i)+2:start(i)+5);
        x(start(i))=char(hex2dec(u));
        x(start(i)+1:start(i)+5)='';
        
    end
end

    
    
end
    