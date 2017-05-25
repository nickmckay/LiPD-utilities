function [yrgo2,yrsp2]=nonan1(X,yr)
% nonan1: longest continuous block of a time series matrix without missing data
% [yrgo2,yrsp2]=nonan1(X,yr);
% Last revised: 2009-10-05
%
% Longest continuous block of a time series matrix without missing data.
% Finds the longest continuous block of rows of a matrix for which none of
% the data is NaN.  Useful in selecting period for calibration of
% tree-ring and climate series.
%
%*** IN 
%
% X (mX x nX)r  time series matrix, mX observations and nX variables
% yr (mX x 1)i  year vector corresponding to X
%
%
%*** OUT 
%
% yrgo2 (1 x 1)i start year of period without any NaN
% yrsp2 (1 x 1)i  end year ...
%
%
%*** REFERENCES -- none
%*** UW FUNCTIONS CALLED -- none
%*** TOOLBOXES NEEDED  -- none
%
%
%*** NOTES
%
% First needed in analyzing GHCN version 2.0 temperature data.  
% Why?  Building database of site information for version 2.0 GHCN temperature
% using v2conv1.m and wanted to include fields for first and last year of 
% longest unbroken period with no missing monthly data. 
%
% Tiebreaker.  If tie for longest unbroken period without NaNs, pick
% the most recent period. For example, say the data covers 1901-31, and that
% all data are valid except for a NaN for some month in 1916.  Periods
% 1901-15 and 1917-31 tie with 15 consecutive years without a NaN.  The
% tiebreaker rule picks 1917, 1931 for yrgo2,yrsp2


[mX,nX]=size(X);
m1 = length(yr);

if mX ~= m1;
    error('yr must be same row size as X');
end

L1 = isnan(X);
L2 =    (any(L1'))'; % logical cv pointing to years with any NaNs

if any(L2)
    i2 = find(L2); % row index for X pointing to the years with NaNs
    i4 = [i2 ; m1+1];
    i3 = [0; i2; m1+1];
    num1 = diff(i3)-1;  % number of 'good' year s in intervals
    [y,i]=max(num1); % maximum consecutive good-year period, and
    % row index into i4 pointing to late-bounding bad year
    
    % If tie for longest unbroken period of good data, take most recent
    Ltie = num1==y;
    if sum(Ltie)>1;
        i = max(find(Ltie));
    end
    yrsp2 = yr(i4(i)-1);
    yrgo2 = yrsp2 - y +1;
else
    yrgo2 = yr(1);
    yrsp2 = yr(m1);
end

  