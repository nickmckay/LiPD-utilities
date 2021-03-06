function newTS=renameTS(TS,filter,useLocal,ask)
%update TS with current meta names
%filter removes entries that don't match a name

%download google name converter

n=fieldnames(TS);

if nargin<3
    load localRenameTS.mat lastSync
    howLong=(now-lastSync)*24*60;
        if howLong<60
            useLocal=1;
        else
            useLocal=0;
        end    
end

if nargin<4
    ask=1;
end

if useLocal
    load localRenameTS.mat goog
else
    goog=GetGoogleSpreadsheet('1C135kP-SRRGO331v9d8fqJfa3ydmkG2QQ5tiXEHj5us');
end

if nargin<2
    filter=0; %don't remove non matches by default
end
for i=1:length(n)
    name=n{i};
    %does it not match the first column?
    if ~any(strcmpi(name,goog(:,1)))
        [name ' isnt a valid name']
        wFlag=1;
        for j=2:size(goog,2)
            ri=find(strcmpi(name,goog(:,j)));
            
            if length(ri)>2
                error(['multiple matches for ' name])
            elseif length(ri)==1
                n{i}=goog{ri,1};
                wFlag=0;
                ['Renaming ' name ' to ' n{i}]
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
               askOverwrite=1;
                    for ne=1:length(notEmpty)
                        %                         if numel(TS(targeti(notEmpty(ne))).(n{i}))~=numel(TS(targeti(notEmpty(ne))).(name))
                        %                             numel(TS(targeti(notEmpty(ne))).(n{i}))
                        %                             numel(TS(targeti(notEmpty(ne))).(name))
                        %                             error([name ' is not the same size as ' n{i} '(entry ' num2str(targeti(notEmpty(ne))) ')'])
                        %                         end
                        if ~strcmp(name,'paleoData_parameter')%for now, don't check for paleoData_parameter
                            if ischar(TS(targeti(notEmpty(ne))).(name))
                                if ~strcmp(TS(targeti(notEmpty(ne))).(n{i}),TS(targeti(notEmpty(ne))).(name)) && askOverwrite
                                    if ask
                                    warning([name ' is trying to overwrite entries in ' n{i} '(entry ' num2str(targeti(notEmpty(ne))) ')'])
                                      answ=input(['Allow ' name ' to overwrite entries in ' n{i} '?']);
                                    else
                                        answ='y';
                                    end
                                      if ~strncmpi(answ,'y',1)
                                          if ask
                                          ans2=input(['Write ' n{i} ' into ' name ' first?']);
                                          else
                                              ans2='y';
                                          end
                                          if ~strncmpi(answ,'y',1)
                                              [TS(targeti).(name)]=TS(targeti).(n{i});
                                              
                                          end
                                      else
                                          askOverwrite=0;
                                      end
                                end
                            elseif iscell(TS(targeti(notEmpty(ne))).(name))
                                
                                
                            else
                                if ~TS(targeti(notEmpty(ne))).(n{i})==TS(targeti(notEmpty(ne))).(name)
                                    if ~strcmp(TS(targeti(notEmpty(ne))).(n{i}),TS(targeti(notEmpty(ne))).(name))
                                        
                                        error([name ' is trying to overwrite entries in ' n{i} '(entry ' num2str(targeti(notEmpty(ne))) ')'])
                                    end
                                end
                            end
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
