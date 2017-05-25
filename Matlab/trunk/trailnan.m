function x=trailnan(x)
% trailnan: remove any trailing NaN's from a vector
% x=trailnan(x);
% Last revised: 2009-10-05
%
% Utility function used by rwlinp.m and other functions. Most users
% will not need to call trailnan in their own code 
%
%*** INPUT
%
% x (1 x ?)r or (? x 1)r vector, usually a time series
%
%*** OUTPUT
%
% x (? x 1)r  the same vector, but with any trailing NaN's removed
%
%*** REFERENCES -- none
%*** UW FUNCTIONS CALLED -- none
%*** TOOLBOXES NEEDED -- none
%
%
%*** NOTES 
%
% If input x is all-NaN, x is returned as []

[mx,nx]=size(x);
if mx==1 && nx>1; % row vector -- to  cv
    j=1; % original is row vector
    x=x';
    mx=nx;
elseif mx>1 && nx==1; % col vector -- ok
     j=2; % original is col vector
else
    error('x must be cv or rv');
end


L1=isnan(x);
sum1=sum(L1);
if sum1==0,
    if j==1;
        x=x';
    end
	return
elseif sum1==mx; % all NaN
    x=[];
    return
else % at least 1 NaN
	if ~isnan(x(mx));  % last value in x is not NaN, so no trailing NaN
        if j==1;
            x=x';
        end
		return
    else % have at least one trailing nan
		fhigh = find(~isnan(x),1,'last'); % row index to last element of  valid data
		iout=(fhigh+1):mx; % want to remove these trailing elements
		x(iout)=[];
        if j==1;
            x=x';
        end
	end
end
