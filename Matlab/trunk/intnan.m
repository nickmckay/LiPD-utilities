function m=intnan(x)
% intnan: check for internal NaN in a vector
% m=intnan(x)
% Last revised 2008-4-29
%
% Utility function for checking whether a vector has an internal, or imbedded, NaN
%
%*** INPUT 
%
% x(? x 1)r or (1 x ?)r  -- a time series
%
%*** OUTPUT 
%
% m(1 x 1)L   1 if x has imbedded NaN, 0 otherwise
%
%*** REFERENCES -- none
%
%
%*** UW FUNCTIONS CALLED -- none
%
%*** TOOLBOXES NEEDED -- none
%
%*** NOTES *********************
%
% Trailing or leading NaN's are not considered internal or imbedded
%
% x=[NaN 4 Nan 2 1 NaN]  has an internal NaN (x(3))
% x=[NaN 4 9 2 1 NaN]  does not have an internal NaN 


[mx,nx]=size(x);
if mx~=1 && nx ~=1, 
	error('x must be a row or column vector')
end

% Convert to rv if needed
if nx==1;
	x=x';
end

L1=~isnan(x);


L2=[0 L1 0];
d = diff(L2);
s1 = sum(d==1);
s2 = sum(d==-1);

if s1>1 || s2>1
	m=1; % the series has an internal NaN
else
	m=0; % the series has no internal NaNs 
end
m=logical(m);
