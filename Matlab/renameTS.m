function newTS=renameTS(TS,filter)
%update TS with current meta names
%filter removes entries that don't match a name

%download google name converter
goog=GetGoogleSpreadsheet('1C135kP-SRRGO331v9d8fqJfa3ydmkG2QQ5tiXEHj5us');

n=fieldnames(TS);

if nargin<2
    filter=0; %don't remove non matches by default
end

for i=1:length(n)
    name=n{i};
    %does it not match the first column?
    if ~any(strcmpi(name,goog(:,1)))
        wFlag=1;
        for j=2:size(goog,2)
            ri=find(strcmpi(name,goog(:,j)));
            
            if length(ri)>2
                error(['multiple matches for ' name])
            elseif length(ri)==1
                n{i}=goog{ri,1};
                wFlag=0;
                break
            end
            
        end
        if wFlag
            warning(['No matches for ' name ])
            if filter
                warning(['Removing ' name ])
                TS=rmfield(TS,name);
            end
        else
            %see if the field already exists
            if isfield(TS,n{i})
                %if exists, are the target cells empty?
                targeti=find(~cellfun(@isempty,{TS.(name)}'));
                if all(cellfun(@isempty,{TS(targeti).(n{i})}))
                    %then replace target cells only
                    [TS(targeti).(n{i})]=TS(targeti).(name);
                    TS=rmfield(TS,name);
                    
                else% see if they're the same
                    notEmpty=find(~cellfun(@isempty,{TS(targeti).(n{i})}) & cellfun(@numel,{TS(targeti).(n{i})})>0);
                    for ne=1:length(notEmpty)
%                         if numel(TS(targeti(notEmpty(ne))).(n{i}))~=numel(TS(targeti(notEmpty(ne))).(name))
%                             numel(TS(targeti(notEmpty(ne))).(n{i}))
%                             numel(TS(targeti(notEmpty(ne))).(name))
%                             error([name ' is not the same size as ' n{i} '(entry ' num2str(targeti(notEmpty(ne))) ')'])
%                         end
                        if ~(strcmp(TS(targeti(notEmpty(ne))).(n{i}),TS(targeti(notEmpty(ne))).(name)) | TS(targeti(notEmpty(ne))).(n{i})==TS(targeti(notEmpty(ne))).(name))
                            
                            error([name ' is trying to overwrite entries in ' n{i} '(entry ' num2str(targeti(notEmpty(ne))) ')'])
                        end
                    end
                    %makes it through, they're all the same overwrite with
                    %confidence
                    [TS(targeti).(n{i})]=TS(targeti).(name);
                    TS=rmfield(TS,name);
                    
                end
            else
                
                [TS.(n{i})]=TS.(name);
                TS=rmfield(TS,name);
            end
        end
        
    end
    
end
newTS=TS;
