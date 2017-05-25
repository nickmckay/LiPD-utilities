function y=rwchng(x,k)
% rwchng: scaled values or scaled first-difference of a time series
% rwchng(x,k);
% Last revised 2003-09-10
% 
% Scaled values or scaled first-difference of a time series.
% Written as utility function for skelcrn.
% The scaled first-difference ring-width or index time series is the
% change in the series from the previous year expressed as a decimal fraction
% of the local level of the series.  The local level is the values of the series
% smoothed by a 9-weight Gaussian filter.<P>
%
%
%*** INPUT ARGS
%
% x (mx x 1) input time series, a ring-width series or index series
% k (1 x 1)i  option for first differencing of time series (see notes)
%   ==1 no first differencing ("local" mode in skelcrn)
%   ==2 first differencing 
%
%*** OUTPUT ARGS
%
% y (my x 1)  scaled first difference of departures
%     my=mx-1
%
%*** REFERENCES -- none
%
%*** UW FUNCTIONS CALLED -- none
%
%*** TOOLBOXES NEEDED
% signal processing
%
%*** NOTES
%
% The algorith depends on choice of the option k.  Both options (k=1 or
% k=2) begin with
%  1. 9-wt Gaussaian low-pass filter the ring widths or indices
%  2. compute departures from low-pass series curve 
% If no first differencing (k=1)
%  3. compute ratio of departure to value of the smooth curve in current
%  year
% If first differencing (k=2)
%  3. compute first difference of departures to accentuate high-frequency change<BR>
%  4. take ratio of first diff of departures to value of the smooth curve in previous year<BR>
%
% The departures (k=1) or first difference of departures (k=2) are expresses as a 
% decimal fraction of the local level of the series, as defined
% by filtering.  The local level is the value of the series is the value smoothed by a 9-weight Gaussian filter:
% 0.0135    0.0477    0.1172    0.2012    0.2408    0.2012    0.1172    0.0477    0.0135
%
%
% filter1.m is used to apply the Gaussian filter to the series.  To handle end effects, the series
% is reflected about its endpoints before filtering. 
%
% The transformation in rwchng.m is useful to build a "crossdating" series representing
% high-frequency variations adjusted to remove effects of differing level of the series.
% With k==2, extremely high frequency variation is emphasized.
%
% k = option for first differencing.  Optional.  If not included, k assumed equal to 2, which calls for first differencing.

mx=length(x);
tx=(1:mx)';

% Design low-pass Filter
%b=fir1(10,.1);  % OBSOLETE.  returns an 11-weigth (n+1) filter with cutoff frequency .05 (20 yrs) 

b=wtsgaus(10,mx); % returns 9-wt Gaussian filter with weights 
% This filter has freq resp 0.90 at 22.2 yr,  0.5 at 8.8 yr, and 0.1 at 4.9
% yr


% Filter the ring width.  

% Formerly used filtfilt this way is the same as 
% convoluting b with itself and then filtering with filter and 
% having to adjust for phase shift.  filtfilt also automatically 
% handles end effects (using reflection across ends).
%
% Now use filter1, again with reflection across endpoints, but no double
% filtering

%g=filtfilt(b,1,x);  
[g,tg]=filter1(x,tx,b,2);

% Departures from smooth curves
d=x-g;


if nargin==1;
    k=2;
else
    if ~any(k==[1 2]);
        error('k not equal to 1 or 2');
    end;
end;


if k==2; %  first-differencing
    % First differences of departures
    f=diff(d);
    
    % Standardized to value of smooth curve in previous year
    gs=g(1:mx-1);
else; % no first-differencing
    f=d;
    gs=g;
    
end;


y=f ./ gs;
t=(1:length(y))';
%plot(t,x(2:length(x)),t,y,t,gs)';
