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
    %if author field is a cell, replace appropriately
    if isfield(bib,'author') & isfield(bib,'title') & (isfield(bib,'year') | isfield(bib,'pubYear'))
        if ischar(bib.author)%if it's a string, convert back to cell
            bib.author=BibtexAuthorString2Cell(bib.author);
        end
        if iscell(bib.author)
            bib.author=authorCell2BibtexAuthorString(bib.author);
        end
    elseif isfield(bib,'type')
        if strcmp(bib.type,'misc')
            miscFlag = 1;
          if isfield(bib,'author') & isfield(bib,'title')  
              if ischar(bib.author)%if it's a string, convert back to cell
                  bib.author=BibtexAuthorString2Cell(bib.author);
              end
              if iscell(bib.author)
                  bib.author=authorCell2BibtexAuthorString(bib.author);
              end
          end
        else
            continue
        end
    else
        continue
    end
    
    %if misc, then assign original data URL to pub URL
    if miscFlag
        if ~isfield(bib,'url')
            if ~isfield(L,'originalDataURL')
                error('Misc entries must of original data URLs, or urls in their pub data')
            else
                
                bib.url = L.originalDataURL;
            end
        end
       %add an institution
       if ~isempty(strfind(bib.url,'noaa.gov'))
           bib.institution = 'World Data Center for Paleoclimatology';
       end
       
    end
    
    %deal with year/pubYear
    if ~miscFlag
        if isfield(bib,'year') && ~isfield(bib,'pubYear')
            bib.pubYear = bib.year;
        end
    end
    
    if(forceNewKey)
        bib=rmfieldsoft(bib,'citeKey');
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
        
        tws = (min(regexp(bib.title,'\W')-1));
        if isempty(tws)
            tws =length(bib.title);
        end
        firstWord = bib.title(1:tws);
        
        
        if ~miscFlag
        if isnumeric(bib.pubYear)
            citeKey=lower([firstAuthor num2str(bib.pubYear) firstWord]);
        else
            citeKey=lower([firstAuthor bib.pubYear firstWord]);
        end
        else
           citeKey=lower([firstAuthor firstWord]);
        end
        %convert accented characters
        citeKey = unicode2alpha(citeKey);
        
        %deal with illegal characters
        citeKey=regexprep(citeKey,'[^a-zA-Z0-9]','');
        
        
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
    
    
    %pub fields to write out.
    toWrite = {'author','journal','pubYear','publisher','title',...
        'volume','DOI','pages','abstract','keywords','url','issue',...
        'institution'};
    
    %bibtex version of those names
    bibNames ={'Author','Journal','Year','Publisher','Title',...
        'Volume','DOI','Pages','Abstract','Keywords','Url','Issue',...
        'Institution'};
    
    doubleBracket = [0 0 0 0 1 0 0 0 1 0 0 0 0];
    
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



