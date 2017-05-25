function Result=c132tss(D)
% c132tss: Thirteen-column monthly climate matrix to time-series structure
% function Result=c132tss(D);
% Last Revised 2009-10-14
%
% Thirteen-column monthly climate matrix to time-series structure.
% Reorganized the 13 cols (year and jan-to-dec data) into 3 columns --
% year, month, data. Reorganized matrix is stored as a field in structure
% Result.  The other fields, designed to hold metadata (e.g., longitude,
% latitude) are not dealt with by c132tss, whose sole function is
% reoroganization of the data matrix.
%
%*** INPUT 
%
% D (mD x nD)r  13-col climate monthly matrix, year as col 1, Jan-Dec as
%   other cols
%
%*** OUTPUT
%
% Result -- structure of results
%   .tsm:  3-col matrix (year, month, data value) of reorganized input D
%
% .... all the other fields (below) are set to dummy values (see notes)
%  Result.units:  units of data--> 'null'
%  Result.names:  cell with station ids --> {'null'}
%  Result.lat:  vector with latitude of stns -->  NaN
%  Result.lon:  vector with longitude...-->  NaN
%  Result.elv:  vector with elevation (m)-->  NaN
%  Result.type  data type (Precip or Tmean) --> 'null'
%  Result.what -- description of fields and history fo generation-->'null'
%  Result.flnames -- cell with names (prefixes) of .mat input files--> {'null'}
%
%*** REFERENCES --- none
%
%*** UW FUNCTIONS CALLED -- none
%
%*** TOOLBOXES NEEDED
%
% stats
%
%
%*** NOTES
%
% Written as utility to convert climate data for use by program seascorr.
% Adapted from more general function (mat2tsss) that filled the various
% fields of structure Result.  User of c132tss is concerned only with
% Result.tsm, and can ignore the other fields of Result. 



[mD,nD]=size(D);
if nD ~=13;
    error('D must be 13-col');
end

yrD = D(:,1);
D(:,1)=[];


if ~all(diff(yrD)==1);
    error('yrD must inc by 1');
end

nyr = length(yrD); % number of years

% Year vector for tss
yr = yrD'; % to row vector
G =  repmat(yr,12,1);
yr = G(:);


% Month vector
j = repmat(((1:12)'),nyr,1);


% Reorganize monthly data
D=D';
d = D(:);

Result.tsm = [yr j d]; 

% Other moot info

 Result.units= 'null';
 Result.names= {'null'};
 Result.lat= NaN;
 Result.lon= NaN;
 Result.elv= NaN;
 Result.type=  'null';
 Result.what='null';
 Result.flnames= {'null'};
