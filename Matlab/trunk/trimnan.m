function [x,yrx]=trimnan(x,yrx)
% trimnan: trim any leading and trailing NaNs from a vector time series
% [x,yrx]=trimnan(x,yrx);
% Last revised: 2009-10-05
%
% Trim any leading and trailing NaNs from a vector time series.
% 
%*** INPUT 
%
% x: time series, a col-vector or row-vector 
% yrx:  year vector, same size as x
%
%
%*** OUTPUT
%
% x: trimmed vector of data
% yrx: trimmed year vector for ouput x
%
%
%*** REFERENCES -- none
%
%*** UW FUNCTIONS CALLED
%
% trailnan
%
%
%*** TOOLBOXES NEEDED -- none
%
%
%*** NOTES 
%
% If input x is all-NaN, x a nd yrx are returned as []

%--- CHECK INPUTS

if isscalar(x) 
    error('x cannot be scalar');
end
if ~isvector(x) || ~isvector(yrx);
    error('x and yrx must be vectors');
end
[mx,nx]=size(x);
[mtemp,ntemp]=size(yrx);
if mx~=mtemp || nx~=ntemp;
    error('x and yrx must be same size');
end


%--- STRIP OF TRAILING AND LEADING NANS

if mx>1; % input is col-vector
    x=trailnan(x);
    if isempty(x);
        yrx=[];
        return
    end
    mx=length(x);
    yrx=yrx(1:mx);
    x=flipud(x);
    yrx=flipud(yrx);
    x=trailnan(x);
    mx=length(x);
    yrx=yrx(1:mx);
    x=flipud(x);
    yrx=flipud(yrx);
else; %  input is row-vector
    x=trailnan(x);
    if isempty(x);
        yrx=[];
        return
    end
    mx=length(x);
    yrx=yrx(1:mx);
    x=flipud(x);
    yrx=flipud(yrx);
    x=trailnan(x);
    mx=length(x);
    yrx=yrx(1:mx);
    x=flipud(x);
    yrx=flipud(yrx);
end
