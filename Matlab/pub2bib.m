function [bigBib,keys,L] = pub2bib(L,forceNewKey)
%write a pub object to a cell in bibtex format to be later written to a
%text file
if nargin==1
    forceNewKey=0;
end

pub = L.pub;
bigBib = cell(length(pub),1);
keys = cell(length(pub),1);
for p = 1:length(pub)
    bib = pub{p};
    miscFlag = 0;
    
    %deal with missing fields
    if isfield(bib,'year') & ~isfield(bib,'pubYear')
        bib.pubYear = bib.year;
    end
    
    if ~isfield(bib,'pubYear')
        bib.pubYear = 0;
    end
    
    if ~isfield(bib,'title')
        bib.title = 'NEEDS A TITLE!';
    end
    
    if ~isfield(bib,'author')
        bib.author = 'NEEDS AUTHORS!';
    end
    
    
    
    %if author field is a cell, replace appropriately
    if ischar(bib.author)%if it's a string, convert back to cell
        bib.author=BibtexAuthorString2Cell(bib.author);
    end
    if iscell(bib.author)
        bib.author=authorCell2BibtexAuthorString(bib.author);
    end
    if isfield(bib,'type')
        if strcmp(bib.type,'misc') | strcmp(bib.type,'dataCitation') | strcmp(bib.type,'online')
            miscFlag = 1;
        end
    end
    
    %if misc, then assign original data URL to pub URL
    if miscFlag
        if ~isfield(bib,'url')
            if ~isfield(L,'originalDataURL')
                %error('Misc entries must of original data URLs, or urls in their pub data')
                bib.url = 'http://need.a.url.here';
            else
                
                bib.url = L.originalDataURL;
            end
        end
        %add an institution
        if ~isempty(strfind(bib.url,'noaa.gov'))
            bib.institution = 'World Data Center for Paleoclimatology';
        end
        
        %force institution to file
        if isfield(bib,'institution')
            bib.title = bib.institution;
        else
            bib=rmfieldsoft(bib,'title');
        end
        
        %assign year to Urldate
        if ~isfield(bib,'Urldate')
            if isfield(bib,'pubYear')
                bib.Urldate = bib.pubYear;
            elseif isfield(bib,'year')
                bib.Urldate = bib.year;
            else
                bib.Urldate = 0;
            end
        end
        bib=rmfieldsoft(bib,{'pubYear','year','title'});
    end
    
    
    


%deal with year/pubYear
if ~miscFlag
    if isfield(bib,'year') && ~isfield(bib,'pubYear')
        bib.pubYear = bib.year;
    end
end

if forceNewKey
    bib=rmfieldsoft(bib,'citeKey');
end

%
if ~isfield(bib,'author')
    bib.author='Author needed';
end

%find citeKey
if isfield(bib,'citeKey')
    citeKey=bib.citeKey;
else
    
    
    aws1 = (min(regexp(bib.author,',')-1));
    aws2 = (min(regexp(bib.author,'\W')-1));
    aws = min([aws1 aws2]);
    
    if isempty(aws)
        aws =length(bib.author);
    end
    firstAuthor = bib.author(1:aws);
    
    
    if miscFlag & ~isfield(bib,'title')
        bib.title = L.dataSetName;
    end
    
    tws = ((regexp(bib.title,'\W')-1));
    if isempty(tws)
        tws =length(bib.title);
    end
    goodTitle = regexprep(bib.title,'[^a-zA-Z0-9]','');
    
    if length(tws)>0
        if all(tws>0) & all(isinteger(tws))
            capTitle = bib.title;
            
            capTitle(tws) = upper(capTitle(tws));
            goodTitle = regexprep(capTitle,'[^a-zA-Z0-9]','');
        end
    end
    shortGoodTitle = goodTitle(1:min(length(goodTitle),25));
    
    
    firstWord = bib.title(1:tws);
    
    
    if ~miscFlag
        if isnumeric(bib.pubYear)
            citeKey=lower([firstAuthor num2str(bib.pubYear) shortGoodTitle]);
        else
            citeKey=lower([firstAuthor bib.pubYear shortGoodTitle]);
        end
    else
        goodUrl = regexprep(bib.url,'[^a-zA-Z0-9]','');
        
        
        if isfield(bib,'Urldate')
            if isnumeric(bib.Urldate)
                citeKey=lower([firstAuthor num2str(bib.Urldate) goodUrl]);
            else
                citeKey=lower([firstAuthor bib.Urldate goodUrl]);
            end
        else
            error('there should be a Urldate');
            citeKey=lower([firstAuthor goodUrl]);
            
        end
    end
    %convert accented characters
    citeKey = unicode2alpha(citeKey);
    
    %deal with illegal characters
    citeKey=regexprep(citeKey,'[^a-zA-Z0-9]','');
    
    %append DataCitation to datacitations
    if isfield(bib,'type')
        if strcmp(bib.type,'misc') | strcmp(bib.type,'dataCitation')
            citeKey=[citeKey 'DataCitation'];
        end
    end
    
    
    bib.citeKey = citeKey;
end

%deal with type
if isfield(bib,'type')
    bibType=bib.type;
    if ~isempty(strfind(bibType,'article'))
        bibType='article';
    end
else
    bibType='article';
end

if miscFlag
    if isfield(bib,'institution')
   bib.title=bib.institution; 
    else
        bib.title='This study';
    end
end


%pub fields to write out.
toWrite = {'author','journal','pubYear','publisher','title',...
    'volume','DOI','pages','keywords','url','issue',...
    'institution','Urldate'};

%bibtex version of those names
bibNames ={'Author','Journal','Year','Publisher','Title',...
    'Volume','DOI','Pages','Keywords','Url','Issue',...
    'Institution','Urldate'};

doubleBracket = [0 0 0 0 1 0 0 0 0 0 0 0 0];

bibOut = cell(1,1);

bibOut{1,1}=['@' bibType '{' citeKey ','];
j=2;
for i=1:length(toWrite)
    if isfield(bib,toWrite{i})
        if isnumeric(bib.(toWrite{i}))
            bib.(toWrite{i})=num2str(bib.(toWrite{i}));
        end
        if doubleBracket(i)
            bibOut{j,1}=[bibNames{i} ' = {{' bib.(toWrite{i}) '}},'];
        else
            bibOut{j,1}=[bibNames{i} ' = {' bib.(toWrite{i}) '},'];
        end
        
        %convert characters to LaTex
        bibOut{j,1} = unicode2latex(bibOut{j,1});
        
        j=j+1;
        
    end
end
lastString =  bibOut{j-1,1};
lastString(end) = '}';
bibOut{j-1,1} =  lastString;

bigBib{p,1}=bibOut;
keys{p,1} = citeKey;
pub{p}=bib;
end
L.pub = pub;


%
%     fid = fopen('test.bib','w');
%     for i=1:size(bibOut,1)
%     fprintf(fid,'%s\n',bibOut{i,1});
%     end
%     fclose(fid);
%
%



