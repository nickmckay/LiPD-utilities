function pre=dirfiles(path1,suff,kopt)
% dirfiles: cell-list of files with specified suffix(es) in a directory
% pre=dirfiles(path1,suff,kopt);
% Last revised 2010-02-18
%
% Cell-list of files with specified suffix(es) in a directory.
% Finds all files with specified suffixes in a directory and returns the
% filenames (without suffix) in fields of structure output variable.
% Example of use would be to make list of all ".rwl" and ".crn" files in
% some directory.
%
%
%*** INPUT
%
% path1 (1 x ?)s  directory of input files
% suff {1x?}s cell array of suffixes of files for which lists desired (no
%       period)
% kopt (1 x 1)i  options
%   kopt(1): case sensitivity of suffixes
%       ==1 case-insensitive
%       ==2 case-sensitive
%
%*** OUTPUT
%
% pre. structure with fields x1, x2, ...
%   Each field has a col-cell array of files with the suffix in suff{1}, suff{2}, etc,
%   or is returned empty (see notes)
%
%*** REFERENCES -- NONE
%*** UW FUNCTIONS  -- NONE
%*** TOOLBOXES -- NONE
%
%*** NOTES
%
% ------Example.  Want names of all ".crn" and ".rwl" files in directory
% "c:\work", and want case-insensitive so that also get them if suffix is
% '.RWL' or '.CRN':
%
% >> pre =dirfiles('C:\work\',{'crn','rwl'},1)
%
% pre.x1 is returned with list of all crn or CRN files
% pre.x2 is returned with ... rwl or RWL files
%-------------
%
% pre.x? is returned as [] if no files with the suffix are found


%--- INPUT CHECK

if ~ischar(path1);
    error(['Input arg ''path1'' must be a string']);
end
if ~isdir(path1);
    error([path1 ' is not a directory']);
end
if ~iscell(suff);
    error(['Input arg ''suff'' must be a cell']);
end

%--- BODY

nsuff=size(suff,2); % number of suffixes

D=dir(path1);  % puts file info into structure D
nfls1 = size(D,1);  % number of files, including directories, in current dir
C=struct2cell(D); % convert structure to cell. C(1,:) holds file names
c = C(1,:); % file names, in cell array
prefx=cell(nfls1,1);

for j = 1:nsuff; % loop over suffixes
    %clear prefx;
    
    suffx=suff{j};
    ncount=0;
    for n = 1:nfls1; % Loop over filenames
        d1 = c{n}; %  a single filename, as char -- could also be a directory
        [pathstr,name,ext,versn] = fileparts(d1);
        if kopt(1)==1; % case-insensitive
            L1 = strcmp(ext,['.' lower(suffx)]);
            L2 = strcmp(ext,['.' lower(suffx)]);
            L3=L1 || L2;
        else
            L3 = strcmp(ext,['.' suffx]);
        end
        if L3;
            ncount=ncount+1;
            d1=name;
            prefx{ncount}=d1;
        else
        end
    end % for over filenames
    if ncount==0;
        eval(['pre.x' int2str(j) '=[];']);
    else
         eval(['pre.x' int2str(j) '=prefx(1:ncount);']);
    end
 end; % for over suffixes


