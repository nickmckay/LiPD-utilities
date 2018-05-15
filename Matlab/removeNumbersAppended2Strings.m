function cc  = removeNumbersAppended2Strings(cc)

for i = 1:length(cc)
    name = cc{i};
    if isstr(name)
        noNum = regexprep(name,'[0-9]','');
        
        tt = find(strcmp(noNum,cc));
        if length(tt)>0
            cc{i} = noNum;
        end
    end
end


