function [I,f,v]=pdgmraw(x,mtaper,npad,kopt)
% pdgmraw: Raw periodogram of tapered and padded time series
% [I,f,v]=pdgmraw(x,mtaper,npad,kopt);
% Last Revised 2009-12-17
%
% Raw periodogram of tapered and padded time series.
% Computes raw periodogram after tapering and padding time series.  Uses
% fast Fourier transform (FFT) for discrete Fourier transform (DFT) and
% computes periodogram such that average ordinate equals variance of 
% original time series. 
%
%
%*** INPUT 
%
% x (mx x 1)r  time series
% mtaper (1 x 1)r decimal proportion of series to be tapered
% npad (1 x 1)n  desired padded length, a power of 2 at least as large as series-length   
% kopt (1 x `1)i  options
%  kopt(1) variance adjustment for tapering and padding
%       ==1 scale variance of tapered and padded variance before DFT 
%       ==2 scale periodogram by factors depending on tapering and padding
%
%*** OUTPUT
%
% I (mI x 1)r periodogram of x, at frequency zero and the Fourier frequencies
% f (mI x 1)r frequencies for I
% v (3x1) variances
%   row 1: original series, x
%   row 2: tapered x
%   row 3: tapered and padded x
%   row 4: average periodogram ordinate (average of I)
%
%*** REFERENCES 
%
%
% Bloomfield, P., 2000. Fourier analysis of time series: an introduction, 
% second edition. John Wiley & Sons, Inc., New York. 261 p.
%
% Ljung, L., 1999. System Identification: Theory for the User (2nd
% Edition). Prentice-Hall, Inc., New Jersey
%
%*** UW FUNCTIONS -- none
%*** TOOLBOXES 
%
% Statistics
%
%
%*** NOTES
%
% Tapering.  Input argument mtaper is the total decimal proportion of the
% series to be tapered. Half of the tapering is at the front end and half
% at the back end.  For example, mtaper==0.10 specifies that 5% of the
% series will tapered at the beginning, and 5% at the end.
% Tapering (by a raised cosine bell) is applied before padding. mtaper must
% be greater than 0 and less 0.40.
%
%
% Tapering and padding impose a complication in that
% they affect the mean and variance of a series. This is handled differently
% depending on kopt(1).
% kopt(1)==1:
%   1) subtract mean
%   2) taper
%   3) re-center to mean 0
%   4) pad with zeros to length npad
%   5) re-scale to variance of original x
%   6) FFT
%   7) periodogram
% kopt(2)
%   1) subtract mean
%   2) taper
%   3) pad
%   4) FFT
%   5) periodogram
%   6) scale periodogram with factor that depends on sum-of-squares of 
%       data window (reflects tapering) and the ratio of padded length 
%       to original length of x.   
%
% Scaling of periodogram.  In the program code, the fulll periodogram is 
% Pyy, with a length of N, where N is the padded length of the time series.
% The variance of the series is directly related to PYY by
%   var(x)= sum(Pyy)/(N-1)
% The part of Pyy returned as the periodogram is I, which is just the first
% N/2+1 elements of Pyy.   This part contains all the information on the
% spectrum, as the N-1 elements of Pyy after dropping off Pyy(1) are
% symmetric. You could compute the variance of the series from I as follows:
%     Ifirst = I(1);
%     Ilast = I(end);
%     Itemp = I(2:(end-1)); % pdgm without its first and last freqs (f=0 and f=0.2)
%     N' = 2*(length(I)-1)-1; % equivalent to npad-1
%     var(x)=(Ifirst+Ilast+2*sum(Itemp))/N';
% This in fact is the variance returned as a check in output v(4)
%  
% The periodogram I returned by pdgmraw.m with kopt(1)==2 may differ 
% in scale from that with kopt(1)==2.  This is because of the different ways
% in which the variance is adjusted to compensate for tapering and padding.
% With kopt(1)==1, the time series after tapering and padding is re-scaled
% to the variance of the original x before proceeeding to FFT and computation
% of periodogram. This ensures that the variance computed from the periodogram
% is equal to the variance of the original time series, x.  If kopt(1)===2,
% the tapered and padded series is subjected to FFT and periodogram
% computation and THEN the periodogram is scaled to compensate for the
% variance reduction due to tapering and padding.  The scaling may 
% result in an over-adjustment or under-adjustment of variance dependng on 
% the actual values of x on the tapered ends.  For example, if those values
% happened to be exactly at the mean of the series, tapering would not
% affect the variance of the series at all, yet the adjustment based on the 
% taper weights would assume a variance reduction.  This is why I prefer
% kopt(1)==1.  But not to make too much of this since the only difference
% is in a constant scaling of the periodogram, which has exactly the same
% shape whether kopt(1)==1 or kopt(1)==2.


%--- CHECK INPUT

% x
if ~(strcmp(class(x),'double') && size(x,2)==1 && size(x,1)>30);
    error('x must be of class double, and col vector of length greater than 30');
end;
if any(isnan(x));
    error('The input series x should not have any NaNs');
end;
mx = length(x);

% mtaper
L=[isscalar(mtaper) isnumeric(mtaper)  (mtaper>0 & mtaper<0.40)];
if ~all(L);
    error('mtaper must be numeric scalar, greater than 0 and less than 0.25')
end

if ~(kopt(1)==1 || kopt(1)==2);
    error('invalid kopt(1)');
end;

% npad
L=[isscalar(npad) isnumeric(npad) mod(npad,1)==0 ];
if ~all(L);
    error('npad must be numeric scalar, and an integer')
end
n2 = nextpow2(mx); % next power of 2 higher than series length
nmin = 2^n2; % padded length must be evenly divisible by this
if mod(npad,nmin)~=0;
    error([num2str(npad) ' not some power of 2 larger than series length ' num2str(mx)]);
end


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
dwin=dwin'; % col vector

% Apply taper
x = x .* dwin; % tapered  mean-subtracted xorig


% RE-SCALE SO THAT MEAN OF TAPERED SERIES EXACTLY ZERO
xmn_taper=mean(x);
x=x-xmn_taper;

% OPTIONALLY COMPUTE VARIANCE-SCALING FACTOR TO COMPENSATE FOR TAPERING
if kopt(1)==2;
    fscale_taper = sqrt(mx/sum(dwin .* dwin)); % scaling factor that would need to be applied
    % to reverse effect of taper on standard deviation of series.  Square root of ratio of
    % sum-of-squares of null window to sum-of-square of taper window
else
    fscale_taper=NaN;
end


%--- PAD WITH ZEROS 
nzeros = npad -mx;
xpad = [x; zeros(nzeros,1)]; % padded, tapered time series

v=[var(xorig) var(x) var(xpad) NaN]; % variance of original, tapered, and tapered+padded; NaN is placeholder for
% mean of periodogram ordinates


%-- OPTIONALLY SCALE VARIANCE OF TAPERED, PADDED SERIES

if kopt(1)==1;
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
else
end


%--- COMPUTE DISCRETE FOURIER TRANSFORM OF TAPERED, PADDED SERIOES
% Note to self:  what follows is same as in  Ljung (1999) notation
% Bloomfield's squared dft is 1/N times Ljung's DFT.

z=fft(xpad,npad);


%--- COMPUTE PERIODOGRAM 
%
% Computation as defined by Ljung (1999) by squaring the DFT. 
% Note: Bloomfield's periodogram is 1/2*pi times Ljung's periodogram.
% Note that sum(Pyy)/(length(xpad)-1) is the variance of the padded series
% xpad.  

Pyy = z.*conj(z)/npad; 

% Pull first half of Pyy as periodogram for plotting.  Frequencies for 
% plot are f=j/npad, where j=0,1,2,...,npad/2, and npad is the padded length
% of the time series.
I=Pyy(1:(npad/2)+1);  % perodogram  at (npad/2)+1 frequencies
nfreq=npad/2+1; % number of frequencies for periodogram
if (mod(nfreq,1)~=0);
    error('nfreq not an integer');
else
    nfreq=floor(nfreq);
end
f=(0.5*linspace(0,1,nfreq))'; % Frequencies for I, as col vector;  f(1) is 
% frequency zero, f(2),...f(nfreq) are the Fourier frequencies of the
% padded series 
vcheck=sum(Pyy)/(npad-1); %  sum-of-squares divided by sample-size-minus-1 should equal variance
Ifirst = I(1);
Ilast = I(end);
Itemp = I(2:(end-1)); % pdgm without its first and last freqs (f=0 and f=0.2)
Ntemp = 2*(length(I)-1)-1; % equivalent to npad-1
v(4)=(Ifirst+Ilast+2*sum(Itemp))/Ntemp; % series variance compute from periodogram I that is returned
d=abs(v(4)-v(1)); % absolute value of differences of periodogram-computed and original variance
if d/v(1)>1E-6; % "too different" mean ratio of difference to original variance greater than 1 millionth
    str1='Periodogram-computed variance too different from actual variance'; 
    error(str1);
end



% OPTIONAL RE-SCALING OF PERIODOGRAM


if kopt(1)==2;
    fscale_pad=  sqrt((npad-1)/(mx-1)); % scaling factor to compensate for padding with zeros
    %  on the standard deviation of a time series
    
    fscale=fscale_pad * fscale_taper; % combined scaling factor to adjust for
    % effects of tapering and padding on standard deviation of a time
    % series
    fscale_var = fscale*fscale;  % corresponding effect on variance
    
    Pyy=Pyy*fscale_var; % scale periodogram
    v(4)=sum(Pyy)/(npad-1); %  sum-of-squares divided by sample-size-minus-1 should equal variance
    I=Pyy(1:npad/2);  % perodogram  at npad/2 frequencies
else
end

