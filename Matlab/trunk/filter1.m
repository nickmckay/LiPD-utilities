function [y,ty]=filter1(x,tx,b,k)
% filter1:  filter a time series, keeping correct phase and adjusting for end effects
% [y,ty]=filter1(x,tx,b,k);
% Last revised 2003-10-31
%
% Filter a time series, keeping correct phase and adjusting for end effects
%
%*** INPUT 
%
% x (mx x 1) time series, no NaN allowed
% tx (mx x 1) time variable
% b (1 x nb) filter weights -- must be odd number of weights
% k (1 x 1)  option for end effects
%   1 - truncate (i.e., use only the observed data)
%   2 - reflect about endpoints -- coded, but not rigorously checked out yet
%   3 - extend with mean of x
%   4 - extend with median of x
%
%
%*** OUTPUT  *************************
%
% y (my x 1) filtered version of x.  my is fewer than mx if k=1
% ty (my x 1) time variable corresponding to y
%
%*** REFERENCES 
%
% Mitchell, J.M., Jr., Dzerdzeevskii, B., Flohn, H., Hofmeyr, 
% W.L., Lamb, H.H., Rao, K.N., and Wallen, C.C., 1966, Climatic change, 
% Technical Note 79: Geneva, World Meteorological Organization.
% 
%*** UW FUNCTIONS NEEDED -- NONE
%
%*** TOOLBOXES NEEDED
%
% signal processing
%
%
%*** NOTES
%
% You must have the filter weights before calling filter1.  One way is
% by trial-and-error with functions such as fir1.m, fltplay2.m
% firdmm2.m to arrive at a filter with desired frequency response.  These 
% steps give the weights b.  Could also merely specify an odd-numbered
% symmetric filter such as a binomial filter or a n-year moving average.
%
%
% Advantage over MATLAB's fltflt.m is that filter1.m avoids having to double-filter 
% the series.  Thus once you get a filter and know its frequency response,
% that is the filter you use, not the filter convoluted with itself.


%*********** SIZE, CHECK AND PREALLOCATE
%
% arguments
if nargin~=4 & nargout~=2,  error('Wrong number of input or output args'), end

% vector sizes
[mx,nx]=size(x);
[mtx,ntx]=size(tx);
if (nx~=1) | (ntx~=1) ; % time series must be col vector
	error('Time series and time-axis variable must be col vectors')
end
if mx~=mtx, error('Time series not same length as time variable'), end;

if any(isnan(x))
    error('filter1 does not allow NaN in x');
end;

% filter length
[mb,nb]=size(b);
if mb~=1, error('Filter weights not a row vector'), end;
if rem(nb,2)~=1, error('Filter has even number of weights'), end;
if (nb > mx), error('Time series less than  length of filter'), end;

% preallocate
xx=zeros(2*nb+mx,1);
tt=zeros(2*nb+mx,1);

noff=fix(nb/2);  % one half of filter length, not counting central value

% Compute vector offset that will apply except when k=1
tb=1;  te=mx;  % beginning and ending times same as for original series
ngo=nb+noff+1;  % Index into appended series of beginning of smoothed series
nstop = ngo+mx - 1;  % index of end...

% Compute prepending and appending sequences
if k==1;  % truncate option -- use only observed data
	ngo=2*nb;
	nstop=mx+nb;
	tb=noff+1; % time of first valid filtered data is shifted forward
	te=mx-noff; % time of last valid ... backwards
	xb=zeros(nb,1); xe = xb;  % startup and after data,  wont actually use these
elseif k==2; % reflect option; reflect around end points
	x1=2*x(1)-x(2:(nb+1));
	xb = x1(nb:-1:1);  
	x2=2*x(mx)-x((mx-nb):(mx-1));
	xe = x2(nb:-1:1);
elseif k==3; % extend with mean
   xb=repmat(mean(x),nb,1);
   xe=xb;
elseif k==4; % extemd with median
   xb=repmat(median(x),nb,1);
   xe=xb;
else;
   error('k =1,2,3,4 only available options');
end;


% Prepend and append
xx=[xb; x;  xe];
tt=[xb; tx; xe];  % Note that xb, xe won't be used here

% Filter the extended version of x
y = filter(b,1,xx);

% Lop off the appropriate end values from the filtered version
y = y(ngo:nstop);
ty=tx(tb:te);

