function [r,SE2,r95]=acf(x,nlags,k)
% acf: autocorrelation function and approximate 95% confidence bands
% [r,SE2,r95]=acf(x,nlags,k);
% Last revised 2008-4-29
%
% Autocorrelation function and approximate 95% confidence bands. Options available
% for plotting and for alternative algorithms of calculation.
%
%*** INPUT ARGUMENTS
%
% x (m x 1) time series, length m
% nlags (1 x 1)i number of lags to compute acf to
% k (1 x 2) options;  <This input argument optional; earlier versions did
%       not include it>
%   k(1) -- plotting
%       ==1 No plotting within function; get this also if no k input
%           argument
%       ==2 Function makes stem plot of acf with CI of +-2 times large-lag
%          standard error
%   k(2) -- alternative algorithms (see Notes)
%       ==1 Uses global means, not means computed separately for subsets of
%           observations, for departures.  Computed covariance as sum of products of first k
%           values and last k values from the the mean.  Then standardizes so
%           that lag 0 autocorrelation is 1.0 by dividing the vector g by g(1),
%           where g is vector of sums of cross-products at lags 0,1,2,... 
%       ==2 Uses subset means and standard deviations in computations
%
%*** OUTPUT ARGUMENTS
%
% r (1 x nlags)r   acf at lags 1 to nlags
% SE2 (1 x nlags)r two times the large-lag standard error of r
% r95 (1 x 1)threshold sample r required for significance in one-tailed test at
%   0.05 alpha (95% signficance).  Intended for quick check for positive first-order 
%   autocorrelation, the most common form of persistence in many natural.
%   If the sample r(1) does not exceed r95, cannot reject H0 that the
%   population r(1) is zero, at 0.05 alpha.  
%   
% <Optional>
%
%*** REFERENCES
%
% Large-lag standard error after Box, G.E.P., and Jenkins, G.M., 1976, Time series 
% analysis: forecasting and control: San Francisco, Holden Day.  
%
% Confidence interval for r(k) from Haan, C.T., 2002, Statistical methods in Hydrology,
% second edition: Ames, Iowa, Iowa State University Press.
%
% Computation formulas for sample r from 
% Wilks, D.S., 1995, Statistical methods in the atmospheric sciences: Academic Press, 467 p.
%
%
%*** UW FUNCTIONS CALLED -- none
%
%
%*** TOOLBOXES NEEDED -- none
%
%
%*** NOTES  
%
% r95 is returned to allow a quick assessment of whether can reject a
% one-sided H0 that population r(1) is zero vs alternative that population
% r(1) is GREATER than 0.  If the sample r(1) exceeds r95, can reject that
% H0.  
%
% Note that r(1) can be significant at 95% in a one-tailed test, and be not
% significant at 95% in a two-tailed test.  The two-tailed test requires
% the test statistic to be further out on the tails of the theoretical
% distribution than the one-tailed test, for the same alpha level
%
% The one-tailed test is of interest because physical systems are often
% characterized by positive persistence, and sometimes you want to specify
% that as the alternative hypothesis
%
% k(2).  This option deals with alternative algorithms.  See Wilks (1995).
% k(2)==1 is the default, and corresponds to computing departures from
% global mean and then standardizing so that r(1) equals 1.0.  This gives
% exactly same result as Matlab toolbox call
%   xcov(x,'coef')
% and corresponds to equation 3.25 in Wilks (1995).
% k(2)==2 corresponds to equation 3.24 in Wilks (1995), and is the less
% simplified algorithm.  Here the departures are from the subperiod means,
% and the denominator is made up of sub-period sums of squares of depatures
% from subperiod means. The optional method of computation are offered
% mainly for instructional purposes -- to show that one can get a different
% autocorrelation depending on the the definition.  Both definitions are
% acceptable.  As the sample size increases, the difference in computed
% autocorrelations becomes less. 
%
% 
%
% Modifications:
%   Original function written in 1991
%   Mod 10/92 to give results for lags 1-M instead of 0-M
%
 

if nargin==2;
    k=[ 1 1];
    khow=1;
else
    if length(k) ~=2;
        error('k, if included as and input argument, should be length 2');
    end
    if ~any(k(1)==[1 2]);
        error('Invalid input arg k(1)');
    end
    if ~any(k(2)==[1 2]);
        error('Invalid input arg k(2)');
    end
    if k(2)==1;
        khow=1; % simple algorithm
    else
        khow=2; % complicatd algorithm
    end
end
    


%*** COMPUTE AUTOCORRELATION FUNCTION

r=subfun01(x,khow);

m=length(x);
r = r(2:(nlags+1));


% 0.05 alpha level of autocorrelation coefficient
r95 = (-1 + 1.6449*sqrt(m-2)) / (m-1);  % for one-tailed test, 95% signif.
%r99 = (-1 + 2.3263*sqrt(m-2)) / (m-1);  % for one-tailed test, 99% signif.



%************   LARGE-LAG STANDARD ERROR   ******************

SE2=repmat(NaN,1,nlags);
for i=1:nlags  % Loop over lags of the acf
	if i==1  ;   %  sum term over lower-lags is zero for lag-1 coefficient
		sum1 = 0;  
	else
		rsub=r(1:i-1);   % make a row vector of acf estimates from lags 1 to i-1
		rsubsq=rsub .* rsub;  % element-by-element multiply to get squares of rsub
		sum1=2*sum(rsubsq);  % sum the squares and multiply by 2, as required in the equation for large-lag standard error
	end
	var=(1/m)  *  (1.0 + sum1);  % variance of ac coef
	SE2(i) = 2.0 * sqrt(var);  % two standard errors
end

if k(1)==2; % plot
   
    klag =[0 (1:length(r))];
    j=klag(2:end);
    rtemp = [1 r];
    stem(klag,rtemp);
    xlabel('Lag');
    ylabel('r')
    lowerlim = -1.0*(max(SE2)+0.05);
    set(gca,'XLim',[-0.5 klag(end)+0.5],'YLim',[lowerlim 1.0]);
    hline1 = line(j,SE2);
    hline2= line(j,-SE2);
    set (hline1,'LineStyle','--','Color',[1 0 0]);
    set (hline2,'LineStyle','--','Color',[1 0 0]);
    txt1='Confidence band is \pm2 large-lag standard errors';
    text(max(klag),max(SE2),txt1,'HorizontalAlignment','Right','Verticalalignment','Bottom')
    title('ACF and 95% Confidence Band')
     
    
else
end


%---- SUBFUNCTIONS 

function r=subfun01(x,khow)
% autocorrelations optionally by different algorithns
if ~isvector(x) || ~isnumeric(x);
    error('x must be vector and numeric')
end
if any(isnan(x));
    error('x cannot have NaN');
end

% if x if rv, transpose to cv
d=size(x);
if d(1)==1;
    x=x';
end
mx=length(x);


%--- make a cv 3 times length of x and put x in middle slots, NaN in others
x1 = repmat(NaN,3*mx,1);
x1((mx+1):(2*mx))=x;

%-- Build index to middle (valid) observations of x1
j1 = ((mx+1): (2*mx))'; % index to middle elements of x1
J1 = repmat(j1,1,mx);

%-- Build a shift index
jj=(0:(mx-1));
JJ =repmat(jj,mx,1);


%--- Build index matrices to first "few" and last "few" obs
Jn = J1-JJ;
Jp = J1+JJ;


%--- Pull first few and last few obs
X1 = repmat(x,1,mx); % just a duped matrix of the valid observations
Xn = x1(Jn); % the first few
Xp = x1(Jp); % the last few


%--- Simple veriosn of conmputation; ala Matlab signal processing toolbox
% xcov(x,'coef')  and Wilks (1995), eqn 3.25

M = repmat(mean(X1),mx,1);
Da = X1-M;
Db = Xn-M;

Dc = Da .* Db;
g = nansum(Dc);
r_simple = g ./ g(1); % autocorrelations lags 0, 1, 2, ....

if khow==1;
    r = r_simple;
    return
end

%--- Compute some subset statistics
Mn = repmat(nanmean(Xn),mx,1); % mean, first few
Mp = repmat(nanmean(Xp),mx,1); % mean, last few
Dn = Xn-Mn; % departures, first few obs from their mean
Dp = Xp-Mp; % departures, last few obs from their mean

%--- SOS of departures
Bn = Dn .* Dn;
bn = nansum(Bn); % for first few obs


%--- row-vector denominator for Wilks, eq 3.24: square root of product of the sos of departures 
% of first few and of last few
c = bn .* bn;
c = sqrt(c);

%--- row-vector numerator for Wilks, eq 3.24: the covariance term
F = (X1-Mn) .* (Dp);
f = nansum(F);


%--- Case of 0 denominator
L = c==0;
c(L)=NaN;

%---- Compute autocorrelation 
r_complicated = f ./ c;
r = r_complicated;


