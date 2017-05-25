function [y,yry]=mafilt1(x,yr,m,kopt)
% mafilt1: evenly-weighted moving average of an annual time series
% [y,yry]=mafilt1(x,yr,m,kopt);
% Last revised 2009-10-05
%
% Evenly-weighted moving average of an annual time series.
% Option for assigning smoothed value to ending year or middle year of the
% moving window
%
%*** INPUT ARGS
%
% x (mx x 1)r time series
% yr (mx x 1)i year vector for x
% m (1 x 1)i length of moving average (e.g.,number of weights)
% kopt (1 x 1)i  options
%   kopt(1) which year of the m-year period to assign smoothed value
%		==1 central year  ==2  ending year
%
%
%*** OUTPUT ARGS
%
% y   (?x1) smoothed time series
% yry (? x1) years for y
%
%
%*** REFERENCES -- NONE
%*** UW FUNCTIONS CALLED -- NONE
%*** TOOLBOXES USED -- NONE
%
%
%*** NOTES
%
% No data extension is used in this function prior to filtering.

%**** Input check

% x and yr must be col vectors of same length
[mx,nx]=size(x);
[myr,nyr]=size(yr);
f=[nx~=1 nyr~=1 mx~=myr];
if any(f);
	clc
	error('x and yr must be col vectors of same length')
end

% yr must increment by 1 each "year"
if ~all(diff(yr)==1);
	clc
	error('yr does not have increment of 1')
end

% m must be positive integer, shorter than x
f=[m<=0  m>=length(x)  rem(m,1)~=0];
if any(f);
	clc
	error('m not postive integer, shorter than x')
end


% kopt must be row vector, length 1
[mkopt,nkopt]=size(kopt);
f=[mkopt~=1  nkopt~=1];
if any(f);
	clc
	error('kopt must be rv of length 1')
end;


% Compute weights
weight=1/m;
b=weight(:,ones(m,1));

% Filter the series
y=filter(b,1,x);  % filtered series, before shifting and truncating

% Compute length of filtered series -- discounting startups and ends
ny=length(yr)-length(b)+1;
i=(0:ny-1)';  % time vector for adding to years

% Compute "plotting" year vector
if kopt(1)==1; % centered moving average
	yr1=yr(1)+(length(b)-1)/2;
	y(1:length(b)-1)=[];
elseif kopt(1)==2; % will want to plot smoothed series at end yr
	yr1=yr(1)+length(b)-1;
	y(1:length(b)-1)=[];
end
yry=yr1+i;

