function r=corrone(y,X)
% corrone: product-moment correlation of one variable with several others
% r=corrone(y,X);
% Last revised 2006-9-2
%
% Correlation coefficients between one variable and several other variables. 
% Written for use as an alternative to corrcoef.m when you do not need the
% full cross-correlation matrix between all variables. Ran about 40 times 
% faster for an example of 1000 time series of length 50 years.
%
%*** INPUT
% 
% y (my x 1)r  key variable; desire correlations between this and all others
% X (mX x nX)r other variables
%
%*** OUTPUT
%
% r (nX x 1)r  product moment correlation between y and all series in X
%
%*** REFERENCES -- none
%*** UW FUNCTION CALLED -- none
%*** TOOLBOXES NEEDED -- none
%
%*** NOTES
%
% y may contain NaNs, but a NaN is not allowed in any X series unless y also NaN that year
%
% corrone.m took 0.22 seconds to get correlations between a 50-yr series y and 1000 
% other series.  Corrcoef took 9.39 seconds for the same task. So corrone is 40+ times 
% as fast as corrcoef for that example.
%
% Revised 2006-9-2 to allow NaNs in y.  But NaN not allowed in X except for years NaN in y

%--- Check input
[my,ny]=size(y);
[mX,nX]=size(X);
if my ~=mX;
   error('X and y must be same row-size');
end;
if ny~=1 || my <2;
   error('y must be a column vector');
end;


% Remove any NaN rows from y, X
L= isnan(y);
if any(L);
    y(L)=[];
    X(L,:)=[];
    [my,ny]=size(y);
    [mX,nX]=size(X);
else
end
if any(any(isnan(X)));
    error('X has a NaN in a year that is not NaN in y');
end


%--- Compute covariance matrix of X
xmean = mean (X);
XM = repmat(xmean,mX,1); % means matrix for X

%-- De-mean X
X1 = X-XM; % X as departures from col means

%-- Compute mean and standard dev of y
ymean=mean(y);


%-- Make a departures matrix of y, same size as X1
ydep = y - ymean;
Y1 = repmat(ydep,1,nX);

%-- Compute covariance matrix of y and X
C1 = Y1 .* X1; % cross products
nsize = repmat(mX-1,1,nX);  % sample size for covariance computation
C2= sum(C1) ./ nsize ; % row vector of sample covariances

%-- Compute standard deviations, sx and sy
sy = std(y);
sy = repmat(sy,1,nX);
sx = std(X); % std devs of X

%-- Compute correlations coefs
r = C2 ./ (sx .* sy);




