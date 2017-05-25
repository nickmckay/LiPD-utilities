function Result=pdgmsim(x,nsim,mtaper,kopt)
% pdgmsim: Exact simulation of Gaussian time series from its periodogram
% Result=pdgmsim1(x,nsim,mtaper,kopt);
% Last Revised 2009-10-27
%
% Exact simulation of Gaussian time series from its periodogram.
% Function coded from Percival and Constantine (2006), using the smoothed-
% periodogram spectral estimator and cirulant embedding following Dietrich
% and Newsam(1997). "Exact" refers to the retetion of the statististical
% properties --- including the spectrum --- of the observed series by the
% simulations. An option allows final scaling of simulations to have same
% and variance as the observed series.  
%
%
%*** INPUT 
%
% x (mx x 1)r  time series
% nsim (1 x 1)n number of simulations desired
% mtaper (1 x 1)r decimal proportion of series to be tapered. Suggest use mtaper=0.10
% kopt (1 x `1)i  options
%  kopt(1) force simulation means and standard deviations to be same as sample
%       ==1 yes
%       ==2 no
%
%*** OUTPUT
%
% Result -- structure of results
%   .Y (mx x nsim)r  time series matrix of simulated time series
%   .I (mx x 1)r  periodogram of x 
%   .var (1 x 3)r variance of original series, tapered series, padded and tapered series
%
%*** REFERENCES 
%
%
% Bloomfield, P., 2000. Fourier analysis of time series: an introduction, 
% second edition. John Wiley & Sons, Inc., New York. 261 p.
%
% Conover, W., 1980, Practical Nonparametric Statistics, 2nd Edition, John
% Wiley & Sons, New York. 
%
% Deitrich, C.R., and Newsam, G.N., 1997. Fast and exact simulation of 
% stationary Gaussian processes through circulant embedding of the 
% covariance matrix. SIAM Journal on Scientific Computing, 18(4): 1088-1107.
%-- shortened to D&N(1997) in comments
%
% Ljung, L., 1999. System Identification: Theory for the User (2nd
% Edition). Prentice-Hall, Inc., New Jersey
%
% Percival, D.B., and Constantine, W.L.B., 2006. Exact simulation of 
% Gaussian time series from nonparametric spectral estimates with 
% application to bootstrapping. Statistics and Computing, 16: 25-35.
%-- shortened to P&C(2006) in comments
%
%
%*** TOOLBOXES NEEDED 
%
% Statistics
%
%*** UW FUNCTIONS CALLED -- none
%
%
%*** NOTES
%
% The method is appropriate for Gaussian distributed time series.  A lilliefors test is applied to the time
% series and the user is flagged (non-fatal) if the assumption of normality is rejected by this test
% at 0.05 alpha.
%
% Approach.  Uses the periodogram (Bloomfield 2000) as a direct spectral estimator
% for the frequency domain weights (P&C 2006, section 3). Uses the D&N (1997) formulation
% to convert the frequency domain weights into a simulated time series (eq
% at top right column on p 27 in P&C (2006)
%
% For simulating time series of length N, requires spectral estimates at 2N frequencies.  Since only N/2 Fourier
% frequencies, use padding with zeros to get series longer than twice it orignal length before Fourier transformation.
% Pad to next highest power of 2 greater than twice the series length.  
% Tapering.  Input argument mtaper is the total decimal proportion of the
% series to be tapered. Half of the tapering is at the front end and half
% at the back end.  For example, mtaper==0.10 specifies that 5% of the
% series will tapered at the beginning, and 5% at the end.
% Tapering (by a raised cosine bell) is applied before padding.
%
% The random component comes into play after estimating the spectral 
% weights.  Standard Gaussian noise is sampled using function normrnd.
%
% Re-scaling of simulations.  Optional re-scaling of simulations is controlled
% by kopt(1).  For some applications it may be desirable for all
% simulations to have exactly the same mean and standard deviation as the
% observed series.  If so, set kopt(1)==1.  On the other hand, if
% kopt(1)==2, the simulations reflect sampling variability in mean and
% variance. It should be noted that the algorithm proceeds by first
% converting the time series to zero mean. The simulations then have means
% that fluctuate around zero.  The sample mean of the observed series is
% added back at the end, so that the simulations have means fluctuating
% around the mean of the observed series. 
%
%
% Revised 2009-10-27. Tapering and padding impose a complication in that
% they affect the mean and variance of a series.  Adjustments for tapering
% and padding are applied in estimation of the periodogram.  Bloomfield
% (2000), for example, applies adjustment factors computed from the
% sum-of-squares of the data window (reflects tapering) and the ratio of
% padded length to original length.   I take another approach, which
% accomplishes the same objective.  That is to scale the variance of the
% tapered and padded series to the variance of the original time series
% before moving on to the discreted Fourier transform.  Following
% Bloomfield (2000), the mean of the observed series is subtracted as an
% initial step before tapering and padding. Between tapering and padding
% with zeros I add an additional step of recentering the tapered series to
% zero mean.  I did this after observing that, depending on the actual
% data, tapering the ends of a zero-mean series may slightly shift the
% mean away from zero.   
%
% Gaussian. The method applies to simulation of Gaussian series.  Expect
% simulations to be non-optimal in some sense (e.g., bias in variance) if
% the original serie is not Gaussian
%
%
% STEPS
%--- check input: time series of length n
%--- subtract series mean; store observed mean
%--- taper the series
%--- recenter the series to zero-mean
%--- pad with zeros to next highest power of 2 greater than twice the 
%       sample length
%--- compute periodogram at fourier frequencies for frequency domain
%       weights s(K) AT FREQUENCIES K= 0/2m,1/2m,...(2m-1)/2m
%--- compute complex valued sequence (top right of p 27, p&c (2006))
%--- use the dft to get pairs of independent realizations of the time time 
%       series (top right of p 27, p&c (2006))
%--- truncate those simulations as needed to get simulations of a desired
%       length
%--- add back the original sample mean of the observed time series
%--- optionally scale the simulations to all have exactly the same mean and
%    variance as the observed time series



%--- CHECK INPUT

if ~(strcmp(class(x),'double') && size(x,2)==1 && size(x,1)>30);
    error('x must be of class double, and col vector of length greater than 30');
end;

if ~(isscalar(nsim) && (strcmp(class(nsim),{'double'}) || isinteger(nsim)) && nsim>=1);
    error('nsim must be scalar, real or integer, and greater than or equal to 1');
end;

if ~(kopt(1)==1 || kopt(1)==2);
    error('invalid kopt(1)');
end;

% Algorithm gives pairs of simulations;  only need to generate half of specified
nsim1 = ceil(nsim/2);

if any(isnan(x));
    error('The input series x should not have any NaNs');
end;

% Gaussian?
knongauss=lillietest(x,.05);
if knongauss ==1;
     uiwait(msgbox('Failed Lilliefors test for normality','Warning','modal'));
end;


%--- SUBTRACT SERIES MEAN

xorig=x;
xmn=mean(x);
xstd=std(x);
x=x-xmn;
mx=length(x);


%--- TAPER THE SERIES

% Taper mtap1/2 of data on each end.  See Bloomfield, p. 84.
% Compute data window
ends= fix((mtaper/2)*mx);
dwin=ones(1,mx);
t=1:ends;
btemp=0.5*(1-cos((pi*(t-0.5))/ends));  %intermediate variable
t=mx-ends+1:mx;
ctemp=0.5*(1-cos((pi*(mx-t+0.5))/ends));  % intermediate

% The data window
dwin(1:ends)=btemp;
dwin(mx-ends+1:mx)=ctemp;



% RE-SCALE SO THAT MEAN OF TAPERED SERIES EXACTLY ZERO
xmn_taper=mean(x);
x=x-xmn_taper;


% OBSOLETE SECTION
% Formerly computed a scaling factor for adjustment of effects of tapering
% from the taper-window weights themselves.  This scaling factor was later
% used along with a factor adjusting for padding to scale the variance of
% the simulations. No longer need this factor because now I explicitly
% scale the tapered padded series to the variance of the original time
% series before taking the DFT
% fscale_taper = sqrt(mx/sum(dwin .* dwin)); % scaling factor that would need to be applied
% to reverse effect of taper on standard deviation of series.  Square root of ratio of
% sum-of-squares of null window to sum-of-square of taper window
%---- end of obsolete


%--- PAD WITH ZEROS TO NEXT HIGHEST POWER OF 2 HIGHER THAN TWICE SAMPLE LENGTH

padlen=2^nextpow2(2*mx);
atemp=padlen-mx;
btemp=zeros(atemp,1);
xpad=[x;btemp]; % padded, tapered time series for analysis period
xvar=[var(xorig) var(x) var(xpad)]; % variance of original, tapered, and tapered+padded



%-- SCALE VARIANCE OF TAPERED, PADDED SERIES

% Scale such that variance of tapered, padded series equals variance of
% original time series
std1 = std(xorig); % standard deviation of original series, before tapering and padding
std2 = std(xpad); % standard dev of tapered, padded series
mn2 = mean(xpad); % mean of tapered padded series
xtemp = xpad-mn2;
xtemp = xtemp * (std1/std2);
xtemp = xtemp+mn2;
xpad=xtemp;
clear std1 std1 mn2 xtemp;


%--- COMPUTE DISCRETE FOURIER TRANSFORM OF TAPERED, PADDED SERIOES
% Note to self:  what follows is same as in  Ljung (1999) notation
% Bloomfield's squared dft is 1/N times Ljung's DFT.

z=fft(xpad,length(xpad));


%--- COMPUTE PERIODOGRAM (section 3.1 in P&C (2006) 
%
% Computation as defined by Ljung (1999) by squaring the DFT. 
% Note: Bloomfield's periodogram is 1/2*pi times Ljung's periodogram.
% Note that sum(Pyy)/(length(xpad)-1) is the variance of the padded series
% xpad.  At least to a scaling factor, Pyy as computed below corresponds to
% S in section 3.1 of P&C (2006).

Pyy = z.*conj(z)/padlen; 
S=Pyy;


%--- SAMPLE GAUSSIAN NOISE AND COMPUTE MU (p 27, top right, P&C (2006))

M=length(xpad)/2; % M will be length of simulated time series before it is truncated
% to the length of the original time series.  Recall that the padded series
%  was padded to length equal to next power of 2 higher than sample length

Z=normrnd(0,1,2*length(xpad),nsim1);  % simulations of noise with mean 0 variance 1, per page 5

k=(1:length(xpad))';
i1 = 2*k-1;
i2=2*k;

term1=Z(i1,:)+i*Z(i2,:); % L term in eqn top of right col, p 27
term2=   sqrt(S/length(xpad)); % R term in eqn top of right col, p 27
term2=repmat(term2,1,nsim1); % column-duplicate the col-vector defined above

mu = term1 .* term2; % finish of the eq


%--- COMPUTE FOURIER TRANSFORM OF MU  
% Pgh below eqn at top right, p 27

V=fft(mu);


%--- EXTRACT THE nsim1 PAIRS OF SIMULATIONS

Vr =real(V);
Vi = imag(V);
D1= Vr(1:M,:);
D2=  Vi(1:M,:);




% OBSOLETE SECTION
% Formerly had to scale simulations by factors related to tapering and
% padding to adjust for variance reduction due to those operations.  Have
% circumvented this by re-scaling the tapered, padded series to have the
% same variance as the observed series BEFORE computing the discrete
% Fourier transform. Thus no longer need these scaling factors
% 
% fscale_pad=  sqrt(length(xpad)/length(x)); % scaling factor to be
%    multiplied by standard deviation of simulations such thad variance
%    is scaled up
% fscale=fscale_pad * fscale_taper; % combined scaling factor to adjust for
%      tapering and padding 
% 
% % Scale the simulations from the real part Vr
% D1mean = repmat(mean(D1),M,1);
% D1std=repmat(std(D1),M,1);
% D1stda = D1std * fscale; % re-scaled standard dev
% D1z = (D1 - D1mean) ./ D1std; % Z-scores
% D1b =  D1z .* D1stda + D1mean;   % Rescaled
% 
% 
% % Scale the simulations from the imag part Vi
% D2mean = repmat(mean(D2),M,1);
% D2std=repmat(std(D2),M,1);
% D2stda = D2std * fscale; % re-scaled standard dev
% D2z = (D2 - D2mean) ./ D2std; % Z-scores
% D2b =  D2z .* D2stda + D2mean;   % Rescaled
%----END OBSOLETE


% RENAME VARIABLES
% Just a convenience to deal with vestigal code from above obsolete section
D1b=D1;
D2b=D2;


%--- REDUCE DIMENSIONS OF SIMULATION MATRIX TO DESIRED LENGTH
% Recall mx is the length of the original time series

D = [D1b D2b];  % each col of D is a simlated time series; but there are more than 
%   nsim simulations (cols), and the lengths of series (number of rows in
%   D) is generally longer than the observed original time series
D = D(1:mx,1:nsim); % truncate accordingly

clear D1 D2 D1mean D1std D1z D1b D2mean D2std D2z D2b



%--- OPTIONAL RESCALING TO FORCE SIMULATIONS TO ALL HAVE THE SAME MEAN AND
% VARIANCE;  THAT IS THE MEAN AND VARIANCE OF THE OBSERVED TIME SERIES.

if kopt(1)==1;
    Dmean = repmat(mean(D),mx,1);
    Dstd = repmat(std(D),mx,1);
    Dz = (D - Dmean) ./ Dstd; % zscores
    D =  (Dz .*  repmat(xstd,mx,nsim)) + xmn;
else
    D=D+xmn; % add original series mean back to simulations
end;


%--- STORE SIMULATIONS, PERIODOGRAM OF ORIGINAL SERIES, AND VARIANCE COMPONENTS

Result.Y=D;
Result.I = Pyy;
Result.var=xvar;

