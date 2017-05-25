function [X,guy,day,pf1]=rwread3(path1,file1)
% rwread3: reads a single .rw file
% [X,guy,day,pf1]=rwread3(path1,file1);
% Last revised 1999-2-15
%
% Reads a single .rw file
% A low-level function called by skelcrn and other
% UW functions.  rwread3.m reads a file of data in ".rw" format,
% and stores the result in a matrix with the year as column 1 and 
% ring width in column 2
% 
%*** INPUT ***********************
%
% path1 (1 x ?)ch path to .rw file
% file1 (1 x ?)ch filename of .rw file
%
%
%*** OUTPUT ************************
%
% X (mX x 2)r year in col 1, ring width in col 2
% guy (1 x ?)ch initials of measurer
% day (1 x ?)ch day measured
% pf1 (1 x ?)ch path\filename of the .rw file
%
%*** REFERENCES -- none
%*** UW FUNCTIONS CALLED --	 none
%*** TOOLBOXES NEEDED -- none
%*** NOTES

pf1=[path1 file1];


% Open rw file for reading
fid = fopen(pf1,'r');

guy=fgetl(fid); % name of measurer
day=fgets(fid);
Lspace=isspace(day);
day(Lspace)=[];


% Read and echo first 2 lines of file.  Line 1 is the measurer;s
% initials.  Line 2 is the date the core was measured.  
disp(pf1);
disp(['   Measured by  '  guy  ' on '  day '.']);

% Read the beginning year for measurements
yrgo = fscanf(fid,'%d',1);

% Read measurements into a cv;
x=fscanf(fid,'%d',inf);
len=length(x);  % How many years of ring width? Still icludes the
	% final 999 value
yr=(yrgo:yrgo+len-1)';  % cv of years

% Delete any 999 rows -- usually just the last row
L=x==999;
x(L,:)=[];
yr(L,:)=[];
if sum(L)==1 & L(length(L))==1,
	disp('   As expected, series has one 999 value')
	disp('   and that is the last value in the series')
	pause(1)
elseif sum(L)==0
	disp('   No trailing 999 value in series -- might be problem')
	disp('   press RETURN to continue');
	pause
elseif sum(L)==1 & L(length(L))~=1,
	error('   Single 999 value in series was not last value')
else
	error('   More than one 999 value read')
end

% Put years in col 1 , measurements in col 2 of X
X=[yr x];

fclose(fid);
