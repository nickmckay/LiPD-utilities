function [pf2,X,yrs,nms]=rwlinp(pf1,path1,path2)
% rwlinp:  read rwl-file data and store in  a .mat file
%  [pf2,X,yrs,nms]=rwlinp(pf1,path1,path2);
% Last revised 2009-9-28
%
% Read rwl-file data and store in  a .mat file.
% Utility function to read an rwo file and store the data in an accessible
% form for MATLAB functions.  Data stored as "index-vector", which is each
% series one after another in a column vector.  <P>
%
%
%*** INPUT (optionally 0-3 args)
%
% pf1 (1 x ?)s <optional> combined path and filename of .rwl file
%   example:  'd:\jack\data\az033.rwl'
% path1 (1 x ?)s <optional> path to the .rwl file.  If this arg is passed, means
%   that pf1 is the filename only
%   Example: 'd:\jack\data\'  as path1,  and   'az033.rwl' as pf1
% path2 (1 x ?)s <optional>, only if also have pf1 and path1>: path
%   for the output .mat files and .tmp files.  If no path2 as argument,
%   default is to the same directory as the .rwl files are in
%
% Input arguments are optional.  There can be 0,1, 2, or 3 input arguments:
%  None: user prompted to clck on names of input and output files
%  One:  combined path & filename for the .rwl file
%  Two: first arg is the filename of the .rwl file, and the second is the path
%  Three: path for the output .mat file; this option is convenienent when user
%    wants .mat output files to go to different directories that that
%    of the source .rwl files
%
%
%*** OUTPUT  
%
% pf2 (1 x ?)s path & filename of output .mat file
% X (? x 1)i  column vector of ringwidths stored one core after another
%	  in units of hundredths of mm
% yrs (? x 3)i start year, end year, and row index of start year of each
%	  core's ring-width series in X
% nms {?x1}s  ids of each core
%
% Depending on the number of input arguments, the output .mat
% file goes to a specified filename or the user is prompted to enter
% it.  The .mat file contains X, yrs and nms, as well as:
%
%   cmask (? x 1)i  mask for core; 1==do not mask, 0==mask.  cmask is created as all 1's
%       by rwlinp.  Subsequent functions may change cmask as cores are deleted from analysis.
%   Fwhen {8 x 4}s   history of fits for the data set.  Casual user need not be concerned with this
%       or cmask.  Fwhen tracks what was the source and target data file, and what and when things were
%       done to the data.
%
% A .tmp ascii file is also produced listing the core id, and first and last years'
% data for each core.  This file intended for checking that rwlinp.m
% indeed stores the ring widths properly
%
%
%*** REFERENCES --none
%
%*** UW FUNCTIONS CALLED
%
% intnan.m  -- checks for internal NaNs in a vector
% trailnan.m -- lops off trailing NaNs from a vector
%
%*** TOOLBOXES NEEDED -- none
%
%*** NOTES
%
% yrs is a matrix with years and row indices that allows retrieval of
% individual ring-width series from the iv X.  The nms are
% stored in the same order as the ring-width series
%
% iv-format storage is expected by several other functions in the
% tree-ring toolbox
%
% Handling of missing values in the .rwl files. Some ITRDB .rwl files
% have blanks for one or more internal years of a time series. In other
% words, the series is not continuous.  rwlinp.m checks for this, and
% warns the user, listing the series name and the violating year(s) on
% the screen.  The output X file will have NaNs in place of such
% missing data.
%
% The core id.  rwlinp.m assumes the core id is in cols 1-8 of every line.
% A new series begins when any character of the the core id changes.
%
% Finding the first year of a ring-width series. rwlinp assumes the
% convention that the "year" on the first decade line of a ring-width
% series corresponds to the first year of data.  Like:
%
% xxxxxx  1867   232   121    45
% xxxxxx  1870   etc    etc  etc  ...
%
% Note the start year above is 1867, and the three values on the first
% line are for 1867,68,69
%
% The end year of a ring-width series.  Assumed to be the last value
% preceding a data field with either all blanks, numeric 999, or numeric -9999
%
%
% Header lines in input .rwl.  ITRDB convention puts 3 header lines
% on the .rwl files.  rwlinp.m handles .rwl files with or without
% the header lines.  Header lines are assumed if the following
% two conditions are satisfied:
%   1. col 8 of the first line in the file contains "1", col
%        8 of line 2 a "2", and col 8 of line 3 a "3"
%   2. lines 9:12 of the first line do not comprise a number
%
% Some Donald Graybill rwl files have 3 header lines that do not follow the above convention.
% The header lines for these files do not necessarily have "1", "2" or "3" in col 8.  This
% is now handled by revision 2005-12-1
%
% A check is made for weird content of first data line (after any headers).  I found that some
% non-ITRDB .rwl files have miscellaneous data in first line.  rwlinp
% checks that cols 9-12 of first data line
% are consistent with being a year.  Col 9-12 must contain a single
% right justified numeric value. Otherwise, error message.
%
% Cols 1-8 generally contain a series code, like "CPE20A1 ", but series starting more than
% 1000 years before AD require 5 cols for the year (e.g., -1500).  Then the year is in cols 1-7.
%
% rwlinp.m is time consuming, but really only needs to be run once for a site.  Then
% the saved .mat file with data in I-V format can be loaded whenever you
% want to access ring widths for use in Matlab.
%
% See special calling program rwlinp1.m (not in toolbox)
% to convert lots of .rwl files at one time
%
%------ assumed form of input .rwl file ---------------------
%	Col 1-7 or 1-8:  Core ID strings.
%	Col 9-12 or 8-12 Year (decade)
%	Col 13-18, 19-24, ... Ring-width values, 10 per line
%
% The rwl file might optionally have a 3-line ITRDB header.  Function finds this
% out as described above
%
% Revised 2005-12-1 to use textread instead of fgetl to read input file
%   and to handle Graybill-specific header lines
% Revised 2006-4-5 to comment out section giving warning if internal NaNs in the ring widths
% Revised 2006-9-1 to include pf2 as output argument for use with slidets
% Revised 2009-8-6 to generalize path/filename code to different OS's
% Revised 2009-8-18 to store nms in row-cell instead of char matrix
% Revised 2009-8-19 additional output arguments added to
%   make function more generally useful (e.g., by rwl2tsm.m)
% 
% tra38:
% Revised 2015-6-9 removed "versn" from output of fileparts (TRA)
%****************************************************************

%--- Hard Code

% Uncomment just 1 of the following statements on debug_level
debug_level=0; % not screen output to track errors (normal situation)
%debug_level=1; % list the rwl filename;  this helps if many files are
%    being processed in a loop by calling program 
%debug_level=2; % list filename and nms as each series is processed 
%debug_level=3; % list filename, nms and data values (each year) 


% Initiate fit history
Fwhen = cell(8,4);
Fwhen{1,1}='rwlinp'; % this function



%***********    GET INPUT .RWL PATH AND FILE NAME
if nargin==0; % interactive version; click on the file
    [fln,path1]=uigetfile('*.rwl','INPUT .rwl file');
    pf1 = fullfile(path1,fln);
    path2=path1; % output to same directory as input .rwl files
elseif nargin==1; % expects this to be the input filename or patH+filename, but
    % if no path assumes in current working directory
    [path1, name, ext] = fileparts(pf1); 
    if isempty(path1);
        eval('path1 = cd;');
        pf1=fullfile(path1,pf1); % build path+filename
        %error(['Argument, ' pathstr ', should not include the path']);
    else
        if ~isdir(path1)
            error(['Could not find directory ' path1]);
        end
    end
    fln=[name ext]; % filename, w/o path
    path2=path1; % assumes output to go to input directory
    
elseif nargin==2 || nargin==3;
    [pathstr, name, ext] = fileparts(pf1); % check that arg1 does not include path
    if ~isempty(pathstr);
        error(['Argument, ' pathstr ', should not include the path if calling witn 2 or 3 arguments']);
    else
    end
    fln=pf1; % filename, w/o path
    if  nargin==2;
        pf1=fullfile(path1,pf1); % build path+filename
        path2=path1; % output file to same dir as input file
    elseif nargin==3; % 3rd argument is assumed to be path2
        pf1=fullfile(path1,pf1); % build path+filename
    end
else
    error('Cannot negative no of in argss');
    
end

% Store name of input rwl file in fit history
Fwhen{1,3}=fln; % infile

% Read the rwl file
F = textread(pf1,'%s','delimiter','\n','whitespace','');

C=char(F);

if debug_level>=1;
    disp(['Input file: ' pf1]); % debug
end

% Initialize
a=NaN;
blnks7=blanks(7);
blnks8=blanks(8);


% Find out if an ITRDB header  (3 lines) in file
c=F{1};
if length(c)<12;
    error('First line in .rwl file ends before col 12')
end
dtemp1 = C(1:3,9:12); % rows 1:3, cols 9:12
dtemp2 = C(4,9:12); % row 4, cols 9:12
dtemp3=  C(1:3,8); % rows 1,3   col 8
if isempty(str2num(dtemp1)) &   isa(str2num(dtemp2),'float'); % This is a Graybill formatted file, with three header lines
    % but not using the convention of 1 ,2, 3 in col 8 of those lines
    C(1:3,:)=[];
    ihead=1; % header lines in original file
    % Header lines gone
elseif all(dtemp3 == ['1';'2';'3']); % A regularly formated rwl with 3 header lines
    C(1:3,:)=[]; Headers gone
    ihead=1; % header lines in original file
else
    yrcheck=str2num(C(1,9:12));
    if isempty(yrcheck) || length(yrcheck)~=1 || isspace(c(12))
        error('Determined no header lines, but cols 9-12 of first data line not a year')
    end
    ihead=0; % no header lines in original file
end
clear dtemp1 dtemp2 dtemp3


%****************  READ PASS THRU DATA TO DETERMINE HOW MANY SERIES, AND
% START AND END ROW OF EACH IN THE DATA FILE

% disp('First pass: counting ring-width series and allocating space'); % debug

% start and end col for data values
jgo=(13:6:67)'; % start col for the 10 data values
jsp=jgo+5;
J1=[jgo jsp];  % start and end col


Ccell= cellstr(C(:,1:8)); % convert id field to col cell of strings
id1 = unique(Ccell); %  col cell of unique names
nsers = length(id1); % number of separate series


%--- Check for nms of zero length, and remove them.  These would be rows with just ctl-Z
ikill= strmatch('',id1,'Exact');
id1(ikill)=[];
nsers = length(id1); % number of separate series

%--- Compute starting and ending row of each series, and number of rows

Nslab = repmat(NaN,nsers,3);
for n =1:nsers;
    idthis=id1{n};
    I=strmatch(idthis,C(:,1:8),'Exact');
    % Check that I (row number for the slab of rows for series) increments by 1
    if ~all(diff(I)==1)
        error(['Series ' idthis ': rows with this id not contiguous']);
    end;
    Nslab(n,:)=[I(1) I(end) (I(end)-I(1)+1)];
    
end;


% Using the total number of lines in the file, and considering 10 years max per
% line, compute an initializing length for the indexed vector
Nlines=Nslab(:,3);
nmax = 10*sum(Nlines);

% Now know this:
%
% nsers is number of series
% Nlines(i) is the number of lines for each series
% Whether or no 3 header lines (ihead==1 vs ihead==0)

% Allocate
nms = cell(nsers,1); % core ids
I=repmat(NaN,nsers,1);
X=repmat(NaN,nmax,1);  % indexed out vector
yrs = repmat(NaN,nsers,3);

%***** Store mask
cmask=ones(nsers,1);


%*************** LOOP OVER SERIES  *****************************


% disp('Second pass: processing the data'); % debug

i=1; % target row in X
for n=1:nsers;
    if debug_level>=2
         disp(['Series #' num2str(n) ':' id1{n}]); % debug
    end
    
    nrows=Nlines(n) ;  % number of decade lines for this core
    rowstart = Nslab(n,1); % starting row of this series in C
    
    I(n)=i; % keep track of row in X of first value for this series
    % Loop over years
    for m = 1:nrows;
        c=C(rowstart+m-1,:); % string data for this row
        if debug_level>=3
            disp(c); % debug
        end
        
        
        % Handle first line
        if m==1;
            nmtemp = c(1:8);
            if nmtemp(8)=='-';
                nmtemp(8)=' ';
                yrslot1=8;
            else
                yrslot1=9;
            end;
           nms{n}=nmtemp;
            yrgo=str2double(c(yrslot1:12));
            
            
            % Compute number years in initial decade
            if yrgo>=0;  % If 0 or A.D.
                ngo=10-rem(yrgo,10);
            else
                ngo=-rem(yrgo,10);
                if ngo==0;  % A year like -310 as first year of decade should give 10 years in line
                    ngo=10;
                end;
                
            end
            
            % Read those years
            for j = 1:ngo;
                jgo=J1(j,1);
                jsp=J1(j,2);
                X(i)=str2double(c(jgo:jsp));
                i=i+1;
            end
            %disp('debug here')
        elseif m<nrows; % handle full decades
            for j=1:10,
                jgo=J1(j,1);
                jsp=J1(j,2);
                %disp(c);
                X(i)=str2double(c(jgo:jsp));
                i=i+1;
            end
            % disp(X(i-1));
        else; % last row. either 10 values, or ends in 999, -9999 or  blanks
            decsp = str2double(c(yrslot1:12));   % decade
            yrsp=decsp-1;  % tentative end year
            k2=1;
            j=1;
            while k2;
                jgo=J1(j,1);
                jsp=J1(j,2);
                if all(isspace(c(jgo:jsp))) || str2double(c(jgo:jsp))==999 ||  str2double(c(jgo:jsp))==-9999 || j>=10;
                    k2=0;
                else
                    X(i)=str2double(c(jgo:jsp));
                    j=j+1;
                    i=i+1;
                    yrsp=yrsp+1;
                end
            end ; % of while k2
        end; % of if m==
    end; % of for m=
    yrs(n,:)=[yrgo yrsp I(n)];
end; % of for n over series


%*********************  CHECK CONSISTENCY OF YEAR RANGES AND ROW COUNTS

I=[I;i]; % running index of start row of series in target vector X
d1=diff(I); % should equal number of years in each series
d2=yrs(:,2)-yrs(:,1)+1; % likewise
d3=d2-d1;
if ~all(d3==0);
    ibad = find(d3~=0);
    nbad = length(ibad);
    nms_suspect = id1(ibad);
    for jbad = 1:nbad;
        disp(nms_suspect{jbad});
    end
    error('Number of years of data inconsistent; Check the series whos ids are listed in the command window')
end

%************** Warning for leading or internal missing values in X
% % Debug
% if isnan(X(1));
% 	disp('Leading NaN(s) in the indexed out vector X');
% 	disp('Press any key to continue')
% 	disp(' ')
% end
%
% Lint=intnan(X);
% if Lint==1; % trouble
% 	for n = 1:nsers;
% 		igo=yrs(n,3);
% 		isp=igo+yrs(n,2)-yrs(n,1);
% 		yr = (yrs(n,1):yrs(n,2))';
% 		x=X(igo:isp);
% 		f=find(isnan(x));
% 		if ~isempty(f); % here is trouble
% 			disp(['Core # ' int2str(n) '(' nms{n} ')']);
% 			disp('   Internal NaN in above series at years:');
% 			disp(yr(f));
% 			disp(' ');
% 			disp('Press any key to continue')
% 			pause
% 			disp(' ');
% 		end
% 	end
% end


%**************** Get rid of any trailing NaNs from X ********

X=trailnan(X);

% Check that length of X consistent with row indices and years
% for last series

ilast = yrs(nsers,3)+yrs(nsers,2)-yrs(nsers,1);
if ilast ~= length(X);
    disp(['yrs vector says X should have row size ' int2str(ilast)]);
    disp(['  X has row size ' int2str(length(X))]);
    error('Row size of X inconsistent with yrs info (see above)');
end


%************************ MAKE OUTPUT FILE *********************

if nargin==0; % interactive version -- prompt for output file name
    txtfile=['.mat output file for ' fln];
    [file3,path3]=uiputfile('*.mat',txtfile);
    pf2 = fullfile(path3,file3);
    [pathstr, name, ext] = fileparts(pf2) ;
    pathtxt=path3;
    
else % automatic verions -- assume .mat with same prefix as .rwl file,
    % and save to same directory as input file
    [pathstr, name, ext] = fileparts(pf1) ;
    pf2=fullfile(pathstr,[name '.mat' ]);
    [pathstr, name, ext] = fileparts(pf2) ;
    pathtxt=pathstr;
end

% Fit history
ctime=clock;
ctime=num2str(ctime(4:5));
dtime=date;
Fwhen{1,2}=[dtime ', ' ctime];
Fwhen{1,4}=[name ext];

% Save output
nms=deblank(nms);
eval(['save ' pf2 ' X ' ' yrs ' ' nms cmask Fwhen;']);


%*************************** MAKE SCREEN OUTPUT OF FIRST, LAST YEARS OFDATA

pftxt=fullfile(pathtxt,[name '.tmp' ]);
fid6=fopen(pftxt,'w');

fprintf(fid6,'%s\n\n','First and Last Years of Ring-Width Data');
for n=1:nsers;
    which=nms{n};
    yrgo=yrs(n,1);
    yrsp=yrs(n,2);
    igo=yrs(n,3);
    isp=igo+yrsp-yrgo;
    xgo=X(igo);
    xsp=X(isp);
    
    str1=sprintf('%3.0f ',n);
    str2=sprintf('%s',which);
    str3=sprintf('%4.0f (%5.0f)   ',yrgo,xgo);
    str4=sprintf('%4.0f (%5.0f)',yrsp,xsp);
    strall=[str1 str2 str3 str4];
    
    fprintf(fid6,'%s\n',strall);
end

fclose(fid6);

