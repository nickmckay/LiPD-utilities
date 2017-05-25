function c=akaike(V,N,m)
% akaike: Akaike information criterion for order of best ARMA model
% c=akaike(V,N,m);
% Last revised  2004-2-17
%
% Akaike information criterion for order of best ARMA model  
%
%*** INPUT ARGUMENTS
%
% V (1 x 1)r loss function, or variance of model residuals
% N (1 x 1)i number of observations
% m (1 x 1)i number of explanatory variables, or sum of AR and MA orders
%
%*** OUTPUT ARGUMENTS
%
% c (1 x 2)r   Akaike information criterion, with and without correction for small sample bias (see
%       notes);  c(1) == with correction; c(2)= without correction
%
%*** REFERENCES
%
% Akaike H. (1974) A new look at the statistical model identification. IEEE Trans. Autom. Control AC-19, 716-723.
% Hurvich C. M. and Tsai C. (1989) Regression and time series model selection in small samples. Biometrika 76, 297-307.
%
%
%*** UW FUNCTIONS CALLED -- none
%
%
%*** TOOLBOXES NEEDED 
%
% System identification
%
%
%*** NOTES  
%
% c.  Correction described by Hurvich and Tsai (1989)


if ~all(size(V)==1) && ~all(size(m)==1) && ~all(size(N)==1);
    error('V ,N and m must be scalar');
end;
if V<0 || m<0 || N<0;
    error('V, m, N must be greater than 0');
end;

c=repmat(NaN,1,2);
c(2)=N*(log(V)+1) + 2*(m+1); % original
c(1) = N*(log(V)+1) + (2*(m+1))* (N/(N-m-2));  % corrected


