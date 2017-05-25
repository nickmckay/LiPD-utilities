function Result=arspectrum(phi,varnoise,nsize,delf,kopt)
% arspectrum: spectrum of an AR(1) or AR(2) process
% Result=arspectrum(phi,varnoise,nsize,delf,kopt);
% Last Revised 2008-3-4
%
% Spectrum of an AR(1) or AR(2) process.  
% Returns the theoretical spectrum as a function of frequency for
% frequencies f for an autoregressive order 1 or 2 process whose
% autoregressive coefficients are in row vector phi. Also requires
% information on the noise variance and series length. 
% 
%
%*** INPUT 
%
% phi(1 x 2)r coefficients of autoregressive model; handles AR(1), AR(2),
%   or white noise (phi(2)==NaN instructs to use AR(1) --see Notes)
% varnoise (1 x 1)r noise variance from fit of the AR model -- see Notes
% nsize (1 x 1)n  number of observations in the time series
% delf (1 x 1)r  frequency interval at which spectrum to be computed;
%   will be at frequencies [0:delf:0.5];  modulus of 0.5 and delf must be 0
% kopt (1 x 2)i options
%   kopt(1):  sign convention on AR coefficients
%       ==1 Ljung (positive autocorrelation goes with NEGATIVE phi(1))
%       ==2 Box and Jenkins (positive autocorrelation goes with positive
%           phi(1)
%   kopt(2): terse vs verbose mode
%       ==1 terse, no graphics
%       ==2 verbose, plot of spectrum in figure 1
%
%
%*** OUTPUT
%
% Result -- structure of results
%   .y spectral estimates at input frequencies Result.f
%   .f col vector of the frequencies
%   .A (1 x 1)r   area under theoretical spectrum, cumputed as sum of delf
%        times spectrum 
%
%*** REFERENCES 
%
% Box, G.E.P., and Jenkins, G.M., 1976, Time series analysis: forecasting 
% and control: San Francisco, Holden Day, p. 575 pp.
%
% Chatfield, C., 1975, The analysis of time series: Theory and practice, Chapman and Hall, London, 263 pp.
%
% Ljung, L. 1995. System identification toolbox; for use with MATLAB, The 
% MathWorks, Inc.
%
% Wilks, D. S., Statistical Methods in the Atmospheric Sciences, 467 p,
% Academic Press, 1995 -- p 352-355
%
%*** TOOLBOXES NEEDED 
%
%*** UW FUNCTIONS CALLED -- none
%
%*** NOTES
% 
% Typically will have previously fit an AR(1) or AR(2) model to the time
% series to get the needed input arguments phi and varnoise. Treetool
% function whit1 can be used for this task.  If wanting red-noise spectrum
% (AR(1)), could alternatively: 1) compute the first-order autocorrelation
% coefficiet as the correlations between the first N-1 and last N-1 values
% of the series, 2) use the relationship varnoise= (1-r1*r1)*var(x), where
% x is the time series and r1 is the coefficient from (1), 3) know that
% ph1(1)is identically r1.
%
% phi.  Second or both of these elements can be NaN.  If both are NaN,
% function returns the white-noise spectrum.  If first element non-zero
% and second element is NaN, assumes desired model is AR(1). Error if 
% first element zeros and second element non-zero. Must also keep in 
% mind the sign conventon on the AR parameters.  This convention differs
% from one time series book or computer package to another.  For example,
% Wilks (1995), Chatfield (1975) and Box and Jenkins (1976) use different
% convention from Ljung (1995).  See kopt.
%

v=varnoise;

%---- ORDER OF AR MODEL

if ~all(size(phi)==[1 2]);
    error('phi must be 1 x 2');
end
if isnan(phi(1)) & ~isnan(phi(2));
    error('phi cannot have NaN as first element and a number as second');
else
    if isnan(phi(1)) & isnan(phi(2));
        j=0; % order is 0
    elseif ~isnan(phi(1)) & ~isnan(phi(2));
        j=2; % AR(2);
    else
        j=1; % AR(1);
    end;
end



%--- FREQUENCY INTERVAL

if ~isscalar(delf);
    error('delf must be scalar');
end
if mod(0.5,delf) ~=0;
    error('delf must divide evenly into 0.5');
end
f=(0:delf:0.5)';
fsize=length(f);



%--- COSINE TERMS and variance term

a= cos(2*pi*f);
b=cos(4*pi*f);
c = 4*v/nsize; % numerator of Bloomfield eqn 8.82, 8.83



%----- COMPUTE SPECTRUM

if j==0; % white noise line
    s1=repmat(c,fsize,1);
    
elseif j==1; % AR(1)
    if kopt(1)==1; %Ljung notation
        denom=1+phi(1).^2+ 2*phi(1)*a;
    else
        denom=1+phi(1).^2 - 2*phi(1)*a;
    end
    s1=c ./ denom;
elseif j==2; % AR(2)
    if kopt(1)==1; %Ljung notation
        denom= 1 + phi(1).^2 + phi(2).^2 + 2*phi(1)*(1+phi(2))*a + 2*phi(2)*b;
    else
        denom= 1 + phi(1).^2 + phi(2).^2 - 2*phi(1)*(1-phi(2))*a - 2*phi(2)*b;
    end
     s1=c ./ denom;
end

%--- AREA UNDER SPECTRUM

A= sum(delf * s1);



%---- OPTIONAL PLOT

if kopt(2)==1; 
else
    figure(1);
    plot(f,s1);
    title(['Area under spectrum is ' num2str(A)]); 
    
    
end

Result.y=s1;
Result.f = f;
Result.A =A;





    






