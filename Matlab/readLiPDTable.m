function cT=readLiPDTable(cT,dirname)

%read in csv
        ncol=sum(cellfun(@(x) length(x.number),cT.columns));
        
        %try to read in as numeric data
        [dirname cT.filename];
        if ~verLessThan('matlab','8.2')
            %use readtable! Requires matlab year >= 13b
            pdTable=table2cell(readtable([dirname cT.filename],'ReadVariableNames',0),'TreatAsEmpty',{'NA','NaN'});
        else
            try
                pdTable=csvread([dirname cT.filename]);
            catch DO
                try%try to read in without header
                    pdTable=csvread([dirname cT.filename],1,0);
                catch DO2
                    %figure out which columns are string and float
                    clear dataType
                    for cc=1:length(cT.columns)
                        if ~isempty(strfind(lower(cT.columns{cc}.dataType),'str'))
                            dataType{1,cc}='%s';
                        else
                            dataType{1,cc}='%f';
                        end
                    end
                    
                    fid=fopen([dirname cT.filename]);
                    [dirname cT.filename]
                    %count how many columns
                    line=fgetl(fid);
                    ncolumn=length(strfind(line,','))+1;
                    while ncolumn > length(dataType)
                        %add str columns to make it work
                        dataType=[dataType {'%s'}];
                    end
                    pdTable=textscan(fid,[strjoin(dataType)],'Delimiter',',','EndOfLine','\n');
                    fclose(fid)
                end
            end
        end
        %check for same number of columns
        if ncol~=size(pdTable,2)
            'WARNING - METADATA and DATA disagree on number of columns!!!!'
            'using minimum of the two'
            I.warnings='METADATA and DATA disagree on number of columns!!!!';
            ncol = min( [length(cT.columns),size(pdTable,2)]);
        end
        %now assign data to columns
        
        for j=1:length(cT.columns)
            
            if iscell(pdTable)
                cT.columns{j}.values=pdTable(:,cT.columns{j}.number);
                if iscell(cT.columns{j}.values);
                    try  cT.columns{j}.values=cell2num(cT.columns{j}.values);
                    catch DO3
                        try  cT.columns{j}.values=cell2mat(cT.columns{j}.values);
                        catch DO4
                        end
                        
                    end
                end
                %don't allow conversion to table of char
                if ischar(cT.columns{j}.values)
                    cT.columns{j}.values=pdTable(:,cT.columns{j}.number);
                end
                
                
            else
                cT.columns{j}.values=pdTable(:,j);
            end
        end
        
        cT=rmfield(cT,'filename');