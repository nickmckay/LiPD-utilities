%treeTS to TS

fnames = fieldnames(treeTS);




for i = 1:length(treeTS)
    
    i=1;
    tts = treeTS(i);
    valLength = length(tts.paleoData_values);
    
    lnames = fnames(structfun(@length,treeTS(1))==valLength);
    
    toMove = setdiff(lnames,'paleoData_values');
    
    newTS = tts;
    for j = 1:length(toMove)
        %create new TS entry, copying tts and then adjusting values, units, variable name...
       newRow = 
       
       %tthen append it to new TS
       newTS = appendStruct(newTS),
    end
    
    %then append to a huge new ts
    
end