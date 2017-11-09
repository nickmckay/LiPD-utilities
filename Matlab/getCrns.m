function allcrns = getCrns(fname)
%read multiple crn in each file
%fname='!AZ.crns';
%fname = 'ak001_crns_tuc.txt';

 file = textread(fname,'%s','delimiter','\n','whitespace','');
maxRowLength = max(cellfun(@length,file));
minRowLength = min(cellfun(@length,file));
if minRowLength<6
   file(find(cellfun(@length,file)<6),:)=[];
end


first6=cellfun(@(x) x(1:6),file,'UniformOutput',0);

%%
%does file start with header?

%find where the firsts 6 change...    
sh = 1;
for i=2:length(first6)
    if ~strcmp(first6{i-1},first6{i})
        sh=[sh; i];
    end
end

%ASSUME THAT ALL EITHER HAVE HEADERS OR NOT....

%have headers?
%max row length?


lastwhitespace = cellfun(@(x) max(regexp(x,['\W'])),file);
mlw = min(lastwhitespace);
second50=cellfun(@(x) x(7:mlw),file,'UniformOutput',0);


isheader = ~cellfun(@isempty,regexp(second50,'[A-Za-z]'));

if any(isheader)
    hasHeaders = 1;
else
    hasHeaders = 0;
end


if hasHeaders %find the starting row of the headers
    sh2 = 1;
    for i=2:length(isheader)
        if isheader(i-1)~=isheader(i)
            if isheader(i)==1
                sh2=[sh2; i];
            end
        end
    end
else
    sh2=sh;%assume that every starting change is a difference
end

%split out the files and load in...

allcrns = cell(1,1);
for n = 1:length(sh2)
    if n<length(sh2)
        [x,s,yr] = crn2vec2(file(sh2(n):(sh2(n+1)-1),:));
            lastRow = file(sh2(n+1)-1,:);
    else
        [x,s,yr] = crn2vec2(file(sh2(n):end,:));
                    lastRow = file(end,:);
    end
    %find if end of row is characters
    endchars = regexp(lastRow{:},'[\D-]+$');
    if ~isempty(endchars)
        allcrns{n}.chronType = regexprep(lastRow{:}(endchars:end),'\W','');       
    end
    
     allcrns{n}.x=x;  allcrns{n}.s=s;  allcrns{n}.yr=yr;
end


%%%TO DO
%2. look for age reversals










