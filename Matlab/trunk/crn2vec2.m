function [x,s,yr]=crn2vec2(pf1)
% crn2vec2:  .crn file to  column vectors of index, sample size, and year
% [x,s,yr]=crn2vec2(pf1)  or [x,s,yr]=crn2vec2;
% Last revised 2009-8-20
%
% Reads a ".crn" file of tree-ring indices in ITRDB format and converts
% the indices and associated data into vectors that can be used in Matlab.
% Input file must be formatted as in ITRDB requirements for crn2vec2 to work.
%
%*** IN
%
% pf1 (1 x ?)s  path and file name of .crn file
%   (e.g., 'c:\work\mt100.crn');
%   alternatively, can call with no input arguments and be prompted to
%   point to the .crn file
%
%*** OUT
%
% x (mx x 1)r   tree-ring index, mx years
% s (mx x 1)r   sample size (number of cores) in each year
% yr (mx x 1)i  year vector for x and s
%
%*** REFERENCES -- None
%
%*** UW FUNCTIONS CALLED -- None
%
%*** TOOLBOXES NEEDED -- None
%
%*** NOTES
%
% The input .crn files are assumed to be in the regular decade-style format used at the
% International Tree-Ring Data Bank (ITRDB), maintained by NOAA.  The URL for obtaining .crn files is :
%
% http://www.ngdc.noaa.gov/paleo/treering.html
%
% The input file usually has header lines with the conventional ITRDB information, and if so the start and stop
% year are taken from header line 2.  They should match the data.
%
% 	Alternatively, some ITRDB files were never submitted with the header info. So the first three lines look like this:
%
% 	co052 -- NO DATA TITLE LINE PROVIDED --               1ST ITRDB LINE MISSING  STD
% 	co052 -- NO DATA TITLE LINE PROVIDED --               2ND ITRDB LINE MISSING  STD
% 	co05 -- NO DATA TITLE LINE PROVIDED --               3RD ITRDB LINE MISSING  STD
%
% 	Not a problem!  If "NO DATA TITLE LINE PROVIDED" is found in the first line, all three header lines are skipped.
% 	In that case, the data lines themselves are used to determine the start and end year of data.
%
% 	A third possibility is no header lines.  If so, the start and end year are again determined from the data. A file is assumed to
%   have no header lines if the block of rows 1-3, cols 7-80 contain ONLY NUMERIC DATA
%
% Revision 4-12-04 handles special case of .crn that does not have a full last decade, but is truncated after
% the last year's sample size rather than 9990-padded.
%
% Revision 2004-9-20 handles special case of .crn file in which BC values coded as negative years AND the year
% begins in col 6 to accomodate the need for 5 digits in the year.
%
% Rev 2008-07-04.  In Istanbul, made two changes for compatibility with tsap
% output rwl:  1) 3 header lines ignored if their length lower than the
% maximum length of any line, 2) last line ignored if its length likewise
%
% Rev 2009-08-20.  In "%---- CHECK LAST LINE OF INPUT; DELETE IF THE FIRST CHAR IS NOT A SPACE,
% LETTER, OR NUMERIC.  THIS TO GET RID OF CTRL-Z LINE".
% The old code would cut off the last line if the first character in that
% line was "0".  That is because isnumeric('0')  returns logical 0.
% Needed to check that ~isempty(str2num(char_last)).  If true, than that
% character is a number.

%--- PRELIMS

xa = repmat(NaN,10,1);  % initialize a 10 element NaN vector to be used later

% -----GET THE  PATH AND FILE NAME OF INPUT FILE -- the .crn file

%NICK ADDED SOMETHING!!!!!
dontskip=1;
if nargin==1
    if ischar(pf1)
        dontskip=1;
    else
        dontskip=0;
    end
end


if dontskip
    % If no input args, screen-click to get .crn file; otherwise path\filename is input argument
    if nargin>1;
        error('Number of input args must be 0 or 1');
    elseif nargin==1; % pf1 has been read as an input argument
        % no action needed
    else;
        [filename,pathname]=uigetfile('*','Input .crn file');
        %[filename,pathname]=uigetfile('*.crn','Input .crn file');
        pf1=[pathname filename];
    end;
    
    %disp(pf1); % debug
    
    % --- READ INPUT FILE AS CELL OF STRINGS
    
    file = textread(pf1,'%s','delimiter','\n','whitespace','');
    
    
    
    
    
    %NICK ADDED!!!
    %bring it in as cell of strings!
else
    file = pf1;
    
end

%-- Rev 5-11-04:   Handle ITRDB lines that end with carriage return
% Delete lines that are all spaces
ff=char(file);
Lsweep = (all(isspace(ff')))';
nsweep=sum(Lsweep);
ff(Lsweep,:)=[];
file=cellstr(ff);


%---- CHECK LAST LINE OF INPUT; DELETE IF THE FIRST CHAR IS NOT A SPACE,
% LETTER, OR NUMERIC.  THIS TO GET RID OF CTRL-Z LINE
char_last = file{end}(1); % first char of last line
if ~(isletter(char_last) | isspace(char_last) | ~isempty(str2num(char_last)));
    file(end)=[];
end;

%--- Rev 4-12-04:  Remove last line if not a true data line, but some
%statistics line with no year; or if the length of the last line is not
%equal to the length of the line before last (Rev 7-03-08
line_year=file{end}(7:10);
if all(isspace(line_year) | (length(file{end}) ~= length(file{end-1})));
    file(end)=[];
end;




%---- FIND OUT IF LEGIT ITRDB HEADER LINES
line1=upper(char(file(1)));
headdummy='NO DATA TITLE LINE PROVIDED';

% Rev 2008-07-04
L1=~isempty(findstr(line1,headdummy)) |  (length(file{1}) ~= size(char(file),2)) |  (length(file{2}) ~= size(char(file),2)) | (length(file{3}) ~= size(char(file),2));


if any(L1); %  ~isempty(findstr(line1,headdummy));
    headtype=2;
    file(1:3)=[]; % strip first 3 lines
    
    % Revised 2004-9-20
    % Find out if special case 5-char year.  If so, some values of col 6 will be '-', and all will be either
    % '-' or blank.  If this special case, set Lyear5==1, otherwise 0
    Htemp = char(file);
    htemp =Htemp(:,6);
    L5a=(strmatch('-',htemp,'exact')); % 1 if any '-' in col 6
    if ~isempty(L5a);
        ncheck1 = length(L5a); % number of rows with '-' on col 6
        L5b=(strmatch(' ',htemp,'exact')); % 1 if any blanks
        if isempty(L5b);
            ncheck2=0;
        else;
            ncheck2=length(L5b);
        end;
        if length(htemp)==(ncheck1+ncheck2);
            Lyear5=1;
        else;
            error('All data rows col 6 do not have either blank or -');
        end;
    else;
        Lyear5=0;
    end;
    
    if Lyear5==1;
        colyr1=6; % first col with year
        colyr2=10; % last cl with year
    else;
        colyr1=7; % first col with year
        colyr2=10; % last cl with year
    end;
    clear Htemp htemp L5a L5b ncheck1 ncheck2 ;
    % End Revised 2004-9-20
    
    
    % Get start year
    c1=file{1}; % first data line
    c2=file{2};
    yrgotemp=str2double(c2(colyr1:10));
    j=findstr(c1,'9990');
    if isempty(j);
        yrgo=yrgotemp-10;
    else;
        yrgo=yrgotemp-(10-length(j));
    end;
    clear yrgotemp c1 c2 j;
    
    % Get end year
    c1=file{end}; % last data line
    c2=file{end-1}; % next to last
    yrsptemp=str2double(c2(colyr1:10));
    j=findstr(c1,'9990');
    if isempty(j);
        yrsp=yrsptemp+19;
    else;
        yrsp=yrsptemp+19-(length(j));
    end;
    clear c1 c2 yrsptemp j;
    
    
elseif  ~any(isletter(line1(7:length(line1))));
    headtype=3;
    
    % Find out if special case 5-char year.  If so, some values of col 6 will be '-', and all will be either
    % '-' or blank.  If this special case, set Lyear5==1, otherwise 0
    Htemp = char(file);
    htemp =Htemp(:,6);
    L5a=(strmatch('-',htemp,'exact')); % 1 if any '-' in col 6
    if ~isempty(L5a);
        ncheck1 = length(L5a); % number of rows with '-' on col 6
        L5b=(strmatch(' ',htemp,'exact')); % 1 if any blanks
        if isempty(L5b);
            ncheck2=0;
        else;
            ncheck2=length(L5b);
        end;
        if length(htemp)==(ncheck1+ncheck2);
            Lyear5=1;
        else;
            error('All data rows col 6 do not have either blank or -');
        end;
    else;
        Lyear5=0;
        
    end;
    
    if Lyear5==1;
        colyr1=6; % first col with year
        colyr2=10; % last cl with year
    else;
        colyr1=7; % first col with year
        colyr2=10; % last cl with year
    end;
    clear Htemp htemp L5a L5b ncheck1 ncheck2 ;
    % End Revised 2004-9-20
    
    
    
    % Get start year
    c1=file{1}; % first data line
    c2=file{2};
    yrgotemp=str2double(c2(colyr1:10));
    j=findstr(c1,'9990');
    if isempty(j);
        yrgo=yrgotemp-10;
    else;
        yrgo=yrgotemp-(10-length(j));
    end;
    clear yrgotemp c1 c2 j;
    
    % Get end year
    c1=file{end}; % last data line
    c2=file{end-1}; % next to last
    yrsptemp=str2double(c2(colyr1:10));
    j=findstr(c1,'9990');
    if isempty(j);
        yrsp=yrsptemp+19;
    else;
        yrsp=yrsptemp+19-(length(j));
    end;
    clear c1 c2 yrsptemp j;
    
else;
    headtype=1;
    file(1:3)=[]; % strip first 3 lines
    
    % Find out if special case 5-char year.  If so, some values of col 6 will be '-', and all will be either
    % '-' or blank.  If this special case, set Lyear5==1, otherwise 0
    Htemp = char(file);
    htemp =Htemp(:,6);
    L5a=(strmatch('-',htemp,'exact')); % 1 if any '-' in col 6
    if ~isempty(L5a);
        ncheck1 = length(L5a); % number of rows with '-' on col 6
        L5b=(strmatch(' ',htemp,'exact')); % 1 if any blanks
        if isempty(L5b);
            ncheck2=0;
        else;
            ncheck2=length(L5b);
        end;
        if length(htemp)==(ncheck1+ncheck2);
            Lyear5=1;
        else;
            error('All data rows col 6 do not have either blank or -');
        end;
    else;
        Lyear5=0;
        
    end;
    
    if Lyear5==1;
        colyr1=6; % first col with year
        colyr2=10; % last cl with year
    else;
        colyr1=7; % first col with year
        colyr2=10; % last cl with year
    end;
    clear Htemp htemp L5a L5b ncheck1 ncheck2 ;
    
    
    % Get start year
    c1=file{1}; % first data line
    c2=file{2};
    yrgotemp=str2double(c2(colyr1:10));
    j=findstr(c1,'9990');
    if isempty(j);
        yrgo=yrgotemp-10;
    else;
        yrgo=yrgotemp-(10-length(j));
    end;
    clear yrgotemp c1 c2 j;
    
    % Get end year
    c1=file{end}; % last data line
    c2=file{end-1}; % next to last
    
    % Rev4-12-04:
    % To handle a crn file that may NOT be 9990-padded on the last line.  In other words, say the last year of
    % data is 2000, and the last line is:
    % BIRWT22000 692 14
    % Approach is to find out how many chars last line is short of 80, and to set the appropriate number of
    % missing values.  For example, if last line has 73 chars, an implicit 9990 is not there for year 2009.
    nfull =length(c2);
    nfinal=length(c1);
    ndrop=nfull-nfinal;
    if ndrop>0; % last line shorter than next to last
        if mod(ndrop,7)~=0; % 7 allows for index and sample size
            error(['last line of crn has ' num2str(nfinal) ' chars; next to last has ' num2str(nfull) '. Difference not evenly divs by 7']);
        end;
        nadjust=ndrop/7;
    else;
        nadjust=0;
    end;
    clear nfull nfinal ndrop;
    % End--  Rev4-12-04:
    
    yrsptemp=str2double(c2(colyr1:10));
    j=findstr(c1,'9990');
    if isempty(j);
        yrsp=yrsptemp+19-nadjust;
    else;
        yrsp=yrsptemp+19-(length(j))-nadjust;
    end;
    clear c1 c2 yrsptemp j nadjust ;
    
end;

yr = (yrgo:yrsp)'; % year vector for output
nyrs = yrsp-yrgo+1; % number of years of data


%--- COMPUTE NUMBER OF "DECADE LINES" OF DATA

%  Note special case handling of negative years.  These occur when series are BC  and the file does not
% use the "add 8000" convention
ii1=yrgo-rem(yrgo,10); % first 'decade'
% Handle the 'negative' starting year case (a la El Malpais)
if rem(yrgo,10)<0;
    ii1=ii1-10; % start year in, say, -136, gives first decade as -140, not -130
end
ii2 = yrsp - rem(yrsp,10);  % ending decade
% Handle 'negative' end year
if rem(yrsp,10)<0;
    ii2=ii2-10;
end
nlines = round(ii2/10)-round(ii1/10) + 1;  % number of 'decade lines' of data


%--- COMPUTE NUMBER OF VALUES EXPECTED ON FIRST AND LAST DECADE LINES

% Compute number of values to skip in reading first decade-line.
% Will differ depending on whether starting year is positive or negative.
% Negative first year example is El Malpais, NM
if yrgo>=0;
    nskip=rem(yrgo,10);
    % Let's say data starts in 1652. Code would say skip first 2 values on "1650" line
else; % negative first year
    nskip = 10 - abs(rem(yrgo,10));
    if nskip==10; nskip=0; end;
    % if yrgo is -139, this says skip one value on the "-140" decade line
end

% Compute number of values to read on last decade line
% Again, different treatment if yrsp is negative
if yrsp>=0;
    nlast = rem(yrsp,10)+1;
    % For example, if yrsp is 1686, says read 7 values -- 1680 to 1686
else;  % yrsp is negative
    nlast = 10 - abs(rem(yrsp,10)) + 1;
    % So if yrsp is -59, says read 2 values (-60 and -59) off last line
    % Or if yrsp is -51, says read 10 values (-60,-59,...,-51) of last line
end


%--- COMPUTE EXPECTED TOTAL NUMBER OF YEARS OF DATA
nyrs = yrsp-yrgo+1;




%--- ALLOCATE STORAGE FOR ROW VECTORS OF INDEX AND SAMPLE SIZE
x=repmat(NaN,nyrs,1); %  index
s=x; %  sample size


%-- COMPUTE TARGET ROW INDICES FOR DATA STORAGE IN x and s
irow=repmat(NaN,nlines,2);
%irow = a(ones(nlines,1),ones(2,1));
irow(:,1) = 1 + 10 * ((0:(nlines-1))');
irow(2:nlines,1) = irow(2:nlines,1) - nskip;
irow(:,2) = irow(:,1)+9;
irow(1,2)=irow(1,2)-nskip;
irow(nlines,2) = nyrs;

% Initialize cols for data and sample size for most lines in the input file
igo1 = [11:7:74];  isp1 = igo1 + 3;  % start, end cols for data
igo2= isp1+1;  isp2 = igo2+2;  % start, end cols for sample size


%--- STORE DATA AND SAMPLE SIZE IN TARGET COLUMN VECTORS

for n= 1:nlines; % Loop over lines of input
    irgo =irow(n,1);
    irsp= irow(n,2);
    c=file{n};  % get a line of data, as string
    
    % Compute start and end positions for the data values and sample size
    ion1=igo1;  ioff1=isp1; ion2=igo2;  ioff2=isp2; nvals=10;
    x1 = xa; s1=xa;  nvals=10;
    
    % Special case if first or last line of data -- may be incomplete decade
    if n==1;
        ion1(1:nskip)=[]; ioff1(1:nskip)=[]; ion2(1:nskip)=[]; ioff2(1:nskip)=[];
        nvals=length(ion1);
    end
    if n==nlines;
        ion1=ion1(1:nlast);  ioff1=ioff1(1:nlast); ion2=ion2(1:nlast); ioff2=ioff2(1:nlast);
        nvals=length(ion1);
    end
    
    x1=xa(1:nvals);
    s1=xa(1:nvals);
    for m = 1:nvals;
        cdat=c(ion1(m):ioff1(m));
        sdat=c(ion2(m):ioff2(m));
        x1(m)=str2double(cdat);
        s1(m)=str2double(sdat);
    end
    x(irgo:irsp)=x1;  % store index in x
    s(irgo:irsp)=s1;   % store sample size in s
end

% HANDLE "8000" CONVENTION

% subtract 8000 from years vector if ending year greater than 2100
if max(yr)>2100;
    yr = yr - 8000;
end


% FLAG 9990s

%   9990 is an ITRDB missing value code; should not be in culled data
Lbad = x==9990;
if any(Lbad);
    str={'Check .crn header year info against true time coverage of valid data',...
        ['9990 value unexpectedly found in some year of ' pf1],...
        ['Expected start and end years :  ' int2str(yrgo) '-' int2str(yrsp)]};
    uiwait(msgbox(str,'Message','modal'));
    kquest=questdlg('Abort Mission');
    if strcmp(kquest,'Yes');
        fclose(fid1);
        error('Aborted because pf 9990 value');
    end;
end;
