function [X,yrX,nms,T]=rwl2tsm(pf1)
% rwl2tsm: ring-width list (rwl) file to time series matrix
% [X,yrX,nms,T]=rwl2tsm(pf1)
% Last revised 2009-9-4
%
% Ring-width list (rwl) file to time series matrix. 
% Reads an rwl file and puts all its ring-width series into a
% time series matrix X with a corresponding year vector yrX.  The columns
% of X correspond to the individual width series in the order they were
% stored in their rwl file.  The row-cell of string names, nms, has the
% core ids of the series in X, in the same order as the columns of X. The
% time series matrix X is filled out with NaNs where data for individual
% series is missing. <P>
%
%
%*** IN
%
% pf1 (1 x ?)s <optional> path and filename of input rwl file(see notes) (e.g.,
%        'c:\data\'az023.rwl');  if not included, you are prompted to point
%        to the file
%
%*** OUT
%
% X (mX x nX)r time series matrix, mX years and nX columns
% yrX (mX x 1)i year vector for X
% nms {size(X,2) x 1}s col-cell of names of series in X
% T (nX x 3)i column, first and last years of valid data in each series of X
%
%*** REFERENCES --- none
%
%*** TOOLBOXES NEEDED -- none
%
%*** UW FUNCTIONS CALLED 
%
% rwlinp
% sov2tsm3
%
%*** NOTES
%
% pf1.  Form of this optional input agrument depends on operating systems.
% For example, in windowx, may have 'c:\data\'az023.rwl', while in Linux
% may have '/dhome/meko/work/az023.rwl'.  If no input argument, user is
% promted to click on an input file 
%       
% The units of X are whatever they are in the rwl file.  Might be
% hundredths of mm, might be thousands of mm, depending on the measuring
% software.  
%
% This function basically is a driver that relies on rwlinp.m 
% to do the work.  See comments to those functions for more
% details
%
% Revised 2009-8-19: call to rwl2sov changed to call to rwlinp


if nargin==1;
elseif nargin==0;
    [file1,path1]=uigetfile('*.rwl','Input ringwidth list (rwl) file');
    pf1=[path1 file1];
else
    error('Must have either no input args or 1')
end


%---- READ THE RWL FILE

[pf2,v,YRS,nms]=rwlinp(pf1);
nms=deblank(nms);


%---- PUT RING WIDTHS IN TIME SERIES MATRIX

[X,yrX,nms]=sov2tsm3(v,YRS,nms,[],[]);
[mX,nX]=size(X);


% Store column-number, first year, last year
j = (1:nX)';
T=[j YRS(:,1:2)];


