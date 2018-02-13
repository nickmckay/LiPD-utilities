%treeTS to TS

fnames = fieldnames(treeTS);


pdfields = fnames(find(~cellfun(@isempty,strfind(fnames,'paleoData_')) | ~cellfun(@isempty,strfind(fnames,'climateInterpretation_'))));

pd2copy = {'paleoData_archiveGenus','paleoData_detrendingMethod','paleoData_googleWorkSheetKey','paleoData_paleoMeasurementTableNumber','paleoData_paleoNumber'}';

pd2rem = setdiff(pdfields,pd2copy);


pd2create = {'paleoData_TSid',
    'paleoData_units',
    'paleoData_values',
    'paleoData_variableName'};

for i = 1:length(treeTS)
    
    tts = treeTS(i);
    valLength = length(tts.paleoData_values);
    
    lnames = fnames(structfun(@length,treeTS(i))==valLength);
    
    toMove = setdiff(lnames,{'paleoData_values','year'});
    
    newTS = tts;
    
    
    newRow = tts; %copy it.
    
    %null out any unneeded fields
    for pdn = 1:length(pd2rem)
        newRow.(pd2rem{pdn}) = [];
    end
    %append row to big
    
    for j = 1:length(toMove)
        %create new TS entry, copying tts and then adjusting regenerating
        %any paleoData_* needed
        
        
        
        %recreate missing fields
        %TSid
        newRow.paleoData_TSid = createTSID(); %generate random TSid (TEMPORARY UNTIL TREE TS IS IMPROVED)
        
        %units
        if strcmp(toMove{j},'ncores')
            newRow.paleoData_units = 'cores'; %they're all unitless
        else
            newRow.paleoData_units = 'unitless';
        end
        
        %values
        newRow.paleoData_values = tts.(toMove{j});
        
        %variableName =
        newRow.paleoData_variableName = toMove{j};
        
        %tthen append it to new TS
        newTS = appendStruct(newTS,newRow);
    end
    
    %then append to a huge new ts
    if i==1
        bigNewTS = newTS;
    else
        bigNewTS = appendStruct(bigNewTS,newTS);
    end
end

%remove treeTS fields
bigNewTSClean = rmfieldsoft(bigNewTS,{'rbar','ncores','eps'});

D = collapseTS1_2(bigNewTSClean);
