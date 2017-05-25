function [G,null_str]=specbt1(z,M,f,prevwind,sername,kopt,tlab)
% specbt1:  spectrum of a single time series  by Blackman Tukey method
% [G,null_str]=specbt1(z,M,f,prevwind,sername,kopt,tlab);
% Last revised 2009-10-22
%
% Compute and optionally plot the sample spectrum with 95% confidence bands. 
% You can interactively control the spectral smoothing through M, the length 
% of the smoothing window.  Figure includes white noise spectral line and 
% bandwidth bar.
%
%*** IN 
%
% z (mz x 1)r  the time series 
% M (1 x 1)i  length of lag window used in calculations.  
% f (mf x 1)r  frequencies (cycles/yr, in range 0-0.5) for spectral estimates
% prevwind(1 x 1)i  previous figure window 
% sername(1 x ?)s   name of series:  for annotating title
% kopt (1 x 2)i or (1x1)i  options
%    kopt(1): whether or not to plot within function 
%      ==1 interactive plotting (linear y) to select final value of M
%      ==2 no plotting; just compute spectrum given initial M
%      ==3 interactive plotting using semilogy plot
%   kopt(2): null-continuum (see notes)
%       ==1 white noise 
%       ==2 red noise
% tlab (time label for frequency (e.g., years^-1)
%
%*** OUT 
%
% G (mG x 5)r   spectrum and related quantities. By column:
%   1- frequency
%   2- period (time)
%   3- spectral estimate
%   4- lower 95% confi limit
%   5- upper 95% conf limit
% null_str: tells what the last col of G is ("white noise" or "red noise"
%
% Graphics output:  
%
% Figure 1.  Spectrum, with 95% confidence interval.  Horizontal line marks
% spectrum of white noise with same variance as z. Horizontal bar marks
% bandwidth of Tukey window used to smooth autocovariance function
%
%*** REFERENCES 
% 
% Chatfield, C. 1975.  Time series analysis, theory and practice.  
% Chapman and Hall, London, 263 p.  
%
% Haan C. T. (2002) Statistical methods in Hydrology, second edition. 
% Iowa State University Press, Ames, Iowa.
%
% Ljung, L. (1987). System Identification: Theory for the User,
% Prentice-Hall, Englewood Cliffs, NJ.
%
% Wilks, D.S., 1995, Statistical methods in the atmospheric sciences:
% Academic Press, 467 p.
%
%
%*** UW FUNCTIONS CALLED
%
% arspectrum -- for red-noise null continuum
% specbt1/calcspec -- subfunction that does most of the meaty calculations
%
%*** TOOLBOXES NEEDED
%
% statistics
% system identification
%
%*** NOTES
%
% More info on the Input:
%
%   M:  Suggest some value on the order of 1/3 to 1/20 of the time series length; 
%   increased M leads to more detail in spectrum, but greater variance of estimates
%
%   f:  Example: [0:.01:.5] gives estimates at freq 0, 0.01, 0.02, ...
%
%   prevwind:  included to allow you to avoid overwriting windows you might have 
%   in the calling program.  If you want spectrum in window 1, just set 
%   prevwind to 0.
%
% Spectrum computed by MATLAB function spa.m, which implements Blackman-Tukey 
% method for spectral estimate (Chatfield 1975).
%
% 95% Confidence interval computed by equation in Chatfield (1975, p 150).  
% Degrees of freedom, following Chatfield, computed as 2.67N/M, where N
% is the sample size and M is the length of the lag window.  Critical points
% of Chi-squared distribution (.025 and .975) computed by call to MATLAB
% function chi2inv.m.
%
% Bandwidth defined in Chatfield (p. 154).  Bandwidth for Tukey window is
% (8 * pi)/(3 * M) in radians.  Using conversion omega=2*pi*f, where omega
% is frequency in radians and f in in cycles per time unit, bandwidth in 
% cycle/unit time is  bw=4/(3M).
%
% Note that spa is in the 'system identification toolbox'. The function description
% says a Hamming window is used to smooth the covariance function.  The Hamming
% window as defined in Ljung (1987, p. 155) is the same as what Chatfield(1975,
% p. 140) calls the Tukey window.
%
% kopt(2) option for null continuum.  If input kopt is scalar, assumes that
% want white noise as null continuum.   If kopt is length 2 with
% kopt(2)==1, also uses white noise as null continuum.  If kopt(2)==2, null
% continuum is red noise, computed as follows: 1) test for significance of
% first-order autocorrelation.  If not significant at 0.05, or if the
% coefficient is negative, revert to a white-noise null continuum.
% Otherwise, fit an AR(1) model and use the theoertical AR spectrum as the
% null continuum.  kopt(2)==3 yields the best-fot AR spectrum up to order AR(2).
% Will revert to white noise spectrum or AR(1) spectrum depending on fit
%
% Significance of first-order autocorrelation. Significance computed as in
% Haan (2002).  For red noise null continuum to be returned rather than 
% white noise, must specify kopt(2)==2 AND the computed sample first order 
% autocorrelation must be positive and greater than 
% (-1 + 1.6449*sqrt(N-2)) / (N-1). This criterion is one-tailed 
% significance test at alpha=0.05.
%
% Revised 2009-10-20. Added option for red noise null continuum, and
% modified to return null continuum (white or red) as a column of G.  Red
% noise null continuum computed as in Wilks (1995), with modifications as
% needed for sign convention of the autoregressive coefficients


nyr = length(z);
defM = min([30 round(nyr)/10]); % default length of lag window

% Subtract mean
z = z - mean(z);


if length(kopt)==1;
    kopt(2)=1; % want white noise null continuum
elseif length(kopt)==2;
else
    error('kopt must be length 1 or 2');
end


% Initial computation and plotting of spectrum
[G,null_str]=calcspec(z,M,f,prevwind,sername,kopt,tlab);

if kopt(1)==2;
   return
end

kinit=1;  % initial setting for default bandwidth

k2=1;
k1 = 1;
while k1~=0;
   k2=menu('Choose 1',...
      'Change Length of Lag Window',...
      'Change y-axis scale',...
      'Accept Spectrum and Quit');
   
   
   switch k2
   case 1
       
       kwhile1=1;
       while kwhile1==1;
           
           prompt={'Enter the value for M:'};
           def={num2str(M)};
           titl='Change Lag Window';
           lineNo=1;
           Mprev=M;
           M=inputdlg(prompt,titl,lineNo,def);
           M=str2num(M{1});
           
           if M>=nyr;
               strmess1 = ['M must be less than ' int2str(nyr)];
               uiwait(msgbox(strmess1,'Rejected!','modal'));
               M=Mprev;
               kwhile1=1;
           elseif (M/nyr)<(1/20) | (M/nyr)>1/3;
               strmess1 = ['Note that M/N=' int2str(M) '/' int2str(nyr) ' is outside the range 1/20 to 1/3'];
               uiwait(msgbox(strmess1,'Warning','modal'));
               kwhile1=0
           else;
               kwhile1=0;
           end;
           
           
       end; % while kwhile1==1;
       
       [G,null_str]=calcspec(z,M,f,prevwind,sername,kopt,tlab);
   case 2; % change scale
       if kopt(1)==1;
         kopt(1)=3;
      elseif kopt(1)==3;
         kopt(1)=1;
      end;
      [G,null_str]=calcspec(z,M,f,prevwind,sername,kopt,tlab);
     
            
   case 3
      k2=0;
      k1=0;
   otherwise
      
   end
   
end

function [G,null_str]=calcspec(z,M,f,prevwind,sername,kopt,tlab)
% kopt (1 x 2)i or (1x1)i  options
% kopt(1): whether or not to plot within function 
%      ==1 interactive plotting (linear y) to select final value of M
%      ==2 no plotting; just compute spectrum given initial M
%      ==3 interactive plotting using semilogy plot
% kopt(2) null line
%   ==1 white noise
%   ==2 red noise (defaulting to white noise if first-order autocorrelation
%       coefficient negative, or if positive but not greater than 0 at
%       alpha=0.05

% This check should not cause a problem because calling function has
% expanded kopt to length 2 from length 1 if needed
if length(kopt)~=2;
    error('kopt must be length 2');
end

N=length(z); % series length

% Compute first-order autocorrelation coefficient
za=z(1:(end-1));
zb =z(2:end);
r1 = corrcoef([za zb]);
r1=r1(1,2);
clear za zb 

% Test that r1 positive and significantly greater than zero (one-tailed
% test) at 0.05 alpha
r1_crit = (-1 + 1.6449*sqrt(N-2)) / (N-1);  % for one-tailed test, 95% signif.

% Should null line be white or red?
Lred = logical(0); % initialized as white
if kopt(2)==2 && r1>r1_crit;
    Lred=1;
end
clear r1_crit




% Convert frequency
w = f * 2 * pi;  

% Compute spectrum;  
g = spa(z,M,w); % freq in col 1, spectrum in col 2 , st dev in col 3

% Manipulations made necessary in MATLAB 6.1 because g is now an iddata object; want freq and spect in g
gfreq=g.Frequency; % col vector of frequency
gspect=g.SpectrumData; % spectrum, in the 3rd dimension
gspect = squeeze(gspect); % spectrum as a cv
clear g;
g=[gfreq gspect];

% need to get freq into col 1 of g, spectrum in col 2
%g(1,:)=[];  % remove first row, which holds variable identifiers

% Frequency from radian units to cycles per year
f = g(:,1)/(2*pi);

% Compute degrees of freedom for Tukey Window
df = round(2.67*N/M);  % see Chatfield (1975, p. 150)

% Find critical points of Chi Squared for 95% confidence interval
c = chi2inv([.025 .975],df);

% Compute confidence interval
clow = df * g(:,2)/c(1);
chi = df * g(:,2)/c(2);

% Store spectal info
nf = length(f);
f1 = f(2:nf);
p1 = 1 ./ f1;
p2 = [inf; p1];
G=[f p2 g(:,2) clow chi];



% White noise line or red noise line
if ~Lred; % white noise
    null_str='white noise';
    G(:,6)=repmat(var(z),nf,1);
else % red noise
    null_str='red noise';
    % Compute variance of the residuals from red-noise model; this
    % straightforward because allowing AR model to be AR(1) only.
    varz=var(z) ; % variance of time series
    vare = varz*(1 - r1*r1); % variance of AR(1) residuals
    
    % Use function arspectrum to get null red noise
    kopt_arspectrum=[2 1]; % use Box-Jenkins sign notation on coefs; terse output
    delf=f(2)-f(1); % frequency interval
    Result_arspectrum=arspectrum([r1 NaN],vare,length(z),delf,kopt_arspectrum);
    
    %--- scale ar spectrum so area under it is same as under white-noise line
    %to same area as sample spectrum
    
    diffcheck=f-Result_arspectrum.f;
    diffmax = max(abs(diffcheck));
    if diffmax>0.00001;
        error('frequencies of spectral estimates not same as of AR spectrum within 0.00001');
    end
    if ~all(g(:,2)>=0);
        error('spectrum has some negative values')
    end
    if ~all(Result_arspectrum.y>=0);
        error('AR null spectrum has some negative values')
    end
    
    scalef = (var(z)*(length(f)-1)) /  sum(Result_arspectrum.y);
    gnull = scalef * Result_arspectrum.y;
    clear diffcheck diffmax scalef varz vare kopt_arspectrum delf Result_arspectrum
       G(:,6)=gnull;
    clear gnull;
end




if kopt(1)==2;
   return
end


% Plot spectrum
figure(prevwind+1);
if kopt(1)==1;
   hspec=plot(f,g(:,2),...
      f,clow,'-r',...
      f,chi,'-r');
elseif kopt(1)==3;
   hspec=semilogy(f,g(:,2),...
      f,clow,'-r',...
      f,chi,'-r');
end;
set(hspec(2),'Color',[1 .5 1]);
set(hspec(3),'Color',[1 .5 1]);
xlabel(['Frequency (' tlab '^{-1})']);
ylabel('Relative Variance');
legend('Spectrum','95% Conf. Interval');

 hline=line(f,G(:,6));
set(hline,'linestyle',':');

%Compute and plot bandwidth
bw = 4/(3*M);  % see Ljung (1987, p. 155), Chatfield (1975, p. 154)
% Note that the "Hamming" window as defined in system ident toolbox and Ljung
% is identical to Chatfield's Tukey Window
% Put bandwidth bar 0.3 from top of figure, centered
ylims = get(gca,'Ylim');
yrng = abs(ylims(2)-ylims(1));
if kopt(1)==1;
    ypoint = ylims(2)-0.3*yrng;
    line([0.25-bw/2 0.25+bw/2], [ypoint ypoint]);
    line([0.25-bw/2  0.25-bw/2],[ypoint+yrng/100 ypoint-yrng/100]);
    line([0.25+bw/2  0.25+bw/2],[ypoint+yrng/100 ypoint-yrng/100]);
    htt = text(0.25,ypoint+yrng/100,'Bandwidth');
elseif kopt(1)==3;
    dlog=log10(ylims(2))-log10(ylims(1));
    dlog5=dlog/5;
    dfact = 10^(-dlog5);
    ypoint = dfact*ylims(2);
    line([0.25-bw/2 0.25+bw/2], [ypoint ypoint]);
    htt = text(0.25,ypoint,'Bandwidth');
end;


set(htt,'HorizontalAlignment','Center','VerticalAlignment','bottom');

% Build title
str1 = sprintf('%4.0f',N); % Length of time series
str2 = sprintf('%4.0f',M); % Width of lag window
str3 = sername; 
title(['Spectrum of ' sername ';  Lag Window \itM/N=\rm ' int2str(M) '/' int2str(N)]);

