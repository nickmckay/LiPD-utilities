function TS = combineInterpretationByScope(TSs)
%combine interpretation by scope

%TS = struct('lengths',size(TSs));

handle = waitbar(0,'combining interpretations...');
for i = 1:length(TSs);
    waitbar(i/length(TSs),handle);
    
    mts = removeEmptyStructureFields(TSs(i));
    fnames = fieldnames(mts);
    %remove preexisting 'interpretationX' fields.
    interpNames = fnames(find(strncmp('interpretation',fnames,14)));
    if length(interpNames)>1
        warning('Removing "interpretationX_*" fields, which were about to create...')
    end
    mts = rmfield(mts,interpNames);
    fnames = fieldnames(mts);
    scopes = {'climate','isotope','ecology','chronology'};
    ti=0;
    for s = 1:length(scopes)
        sts = [scopes{s} 'Interpretation'];
        
        %how many scopes with this interpretation?
        ss = [ sts '[0-9]'];
        intnumcell = uniqueCell(cellfun(@(x) x(regexp(x,ss,'end')), fnames,'UniformOutput',0));
        %remove empty
        ie = find(~cellfun(@isempty,intnumcell));
        intnumcell = intnumcell(ie);
        nInterp = max(cellfun(@str2num, intnumcell));
        if length(nInterp)>0
            for ni = 1:nInterp
                ti = ti+1;
                %find all the interpretation keys
                ssn = [ sts num2str(ni)];
                names = fnames(find(~cellfun(@isempty,cellfun(@(x) x(regexp(x,ssn)), fnames,'UniformOutput',0))));
                for n = 1:length(names)
                    thisname = names{n};
                    postUnderscore = thisname(strfind(thisname,'_')+1:end);
                    mts.(['interpretation' num2str(ti) '_' postUnderscore]) = mts.(thisname);
                end
                mts.(['interpretation' num2str(ti) '_scope']) = scopes{s};
                mts = rmfield(mts,names);
            end
            
        end
    end
    %TS(i) = mts;
    if ~exist('TS')
        TS = mts;
    else
        TS = appendStruct(TS,mts);
    end
end

delete(handle)
TS = structord(TS);

end

