function [ newname ,changed] = convertName(field,name)
%converts variable name to standardized name
load nameCon.mat

if ~exist('lastUpdated')
   lastUpdated =  0;
end

if ((now-lastUpdated)*1440)>30
    updateNameConverterFromGoogle;
end

if ischar(name)
    
    
    %check parameter name
    if ~isfield(nameCon,field)
        error([field ' has no entries in nameCon.mat']);
    end
    
    %check to make sure all cells are unique within field
    %TBD
    
    %check to see if the name matches a parameter name
    standardNames=cellfun(@(x) x.acceptedName, nameCon.(field),'UniformOutput',0);
    
    if any(strcmpi(name,standardNames))
        newname=standardNames{find(strcmpi(strtrim(name),standardNames))};
        changed=0;
    else
        for i=1:length(standardNames)
            if any(strcmpi(strtrim(name),nameCon.(field){i}.alternates))
                newname=standardNames{i};
                break
            elseif i==length(standardNames)
                warning([strtrim(name) ': no name was recognized, keeping original'])
                newname=name;
            end
        end
        changed=1;
        
    end
elseif iscell(name)
    newname=cell(length(name),1);
    changed = zeros(length(newname),1);
    for n=1:length(name)
        %check parameter name
        if ~isfield(nameCon,field)
            error([field ' has no entries in nameCon.mat']);
        end
        
        %check to make sure all cells are unique within field
        %TBD
        
        %check to see if the name matches a parameter name
        standardNames=cellfun(@(x) x.acceptedName, nameCon.(field),'UniformOutput',0);
        
        if any(strcmpi(name{n},standardNames))
            newname{n}=standardNames{find(strcmpi(strtrim(name{n}),standardNames))};
        else
            for i=1:length(standardNames)
                if ~isempty(name{n})
                    if ~ischar(name{n})
                        if iscell(name{n})
                            name{n} = stringifyCells(name{n});
                        elseif isnumeric(name{n})
                            name{n} = num2str(name{n});
                        
                        end
                        
                    end
                    if any(strcmpi(strtrim(name{n}),nameCon.(field){i}.alternates))
                        newname{n}=standardNames{i};
                        changed(n)=1;
                        break
                    elseif i==length(standardNames)
                        warning('no name was recognized, keeping original')
                        newname{n}=name{n};
                    end
                else
                    newname{n}=name{n};
                end
            end
        end
    end
else%do nothing
    newname=name;
    
end

