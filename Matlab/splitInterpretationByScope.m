function  TS = splitInterpretationByScope(TS)

for i = 1:length(TS)
    display(i)
    mts = TS(i);
    fnames = fieldnames(mts);
    intnumcell = uniqueCell(cellfun(@(x) x(regexp(x,'interpretation[0-9]','end')), fnames,'UniformOutput',0));
          nInterp = max(cellfun(@str2num, intnumcell(2:end)));

    if nInterp>1%there are some!
        
        scopeType =cell(1,2);
        for n = 1:nInterp
            %figure out what scope and what scope number
            thisScope = mts.(['interpretation' num2str(n) '_scope']);
            if n==1
                scopeType{1,1} = thisScope;
                scopeType{1,2} = 1;
                thisNum =  scopeType{1,2};
            else
                ws = find(strcmp(scopeType(:,1),thisScope));
                if length(ws)>0
                    scopeType{ws,2} = scopeType{ws,2}+1;
                    thisNum =  scopeType{ws,2};
                else
                    scopeType{size(scopeType,1)+1,1} = thisScope;
                    scopeType{size(scopeType,1),2} = 1;
                    thisNum =  1;
                end
            end
            
            %loop through all the variables in the interpretation and assign
            
            sch = ['interpretation' num2str(n) '_'];
            ti = find(strncmp(fnames,sch,length(sch)));
            for t = 1:length(ti)
                thisKeyName = fnames{ti(t)};
                thisKeyName = thisKeyName(length(sch)+1:end);
                thisKey = mts.([sch thisKeyName]);
                if ~isempty(thisKey)
                    %WRITE IT!!!
                  %  display(['writing TS.' thisScope 'Interpretation' num2str(thisNum) '_' thisKeyName])
                    [TS(i).([thisScope 'Interpretation' num2str(thisNum) '_' thisKeyName])] = thisKey;
                end
            end   
        end
    end
end

TS = structord(TS);

end