function cT=readLiPDTable(cT,dirname)

newMethod = 1;%use read table if possible

%read in csv
%check that number exists in all.
mN = 0;
for i = 1:length(cT.columns)
    if isfield(cT.columns{i},'number')
        mN = max(mN,max(cT.columns{i}.number));
    else
        cT.columns{i}.number = mN+1;
    end
end

ncol=sum(cellfun(@(x) length(x.number),cT.columns));
%try to read in as numeric data
%[dirname cT.filename]
if ~verLessThan('matlab','8.2') & newMethod
    %use readtable! Requires matlab year >= 13b
    if ~strcmpi(cT.filename((end-3):end),'.csv')
        cT.filename=[cT.filename '.csv'];
    end
    if isfield(cT,'missingValue')
        missingValues = {'NA','NaN',cT.missingValue};
    else
        missingValues = {'NA','NaN'};
    end
    
    pdTable=table2cell(readtable([dirname cT.filename],'ReadVariableNames',0),'TreatAsEmpty',missingValues);
    empties =~cellfun(@isempty,pdTable);
    %remove any empty cols and rows
    pdTable = pdTable(sum(empties,2)>0,sum(empties,1)>0);
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
    warning('WARNING - METADATA and DATA disagree on number of columns!!!!');
    display('using minimum of the two')
    I.warnings='METADATA and DATA disagree on number of columns!!!!';
    ncol = min( [length(cT.columns),size(pdTable,2)]);
end
%now assign data to columns

for j=1:length(cT.columns)
    if cT.columns{j}.number<=size(pdTable,2) %probably improve this in teh future
        
        if iscell(pdTable)
            cT.columns{j}.values=pdTable(:,cT.columns{j}.number);
            if iscell(cT.columns{j}.values);
                try  cT.columns{j}.values=cell2num(cT.columns{j}.values);
                catch DO3
                    try  cT.columns{j}.values=cell2mat(cT.columns{j}.values);
                    catch DO4
                        try  cT.columns{j}.values=forceCell2Mat(cT.columns{j}.values);
                        catch DO5
                        end
                        
                        
                        
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
end

cT=rmfield(cT,'filename');