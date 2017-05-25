function b=wtsbinom(a,kopt)
% wtsbinom: weights for binomial filter of desired length or 50% response period
% b=wtsbinom(a,kopt);
% Last revised 2003-03-27
%
% Weights for binomial filter of desired length or 50% response period<P>
%
%*** INPUT
%
% a (1 x 1)i  desired number of weights or periof of 50% response . See kopt.
% kopt(1 x 1)i option
% kopt(1)==1   a is the period for which amp of freq response should be 0.5
% kopt(1)==2   a is the number of weights (odd, central + both sides desired)
%
%*** OUTPUT
%
% b (1 x n)r  computed weights (see notes)
% 
%*** REFERENCES
% 
% Panofsky, H. and Brier, G., 1958.  Some applications of statistics to 
% meteorology.  The Pennsylvania State University.  p. 150.
% 
% Mitchell et al. (1966, p. 47)
%
%*** UW FUNCTIONS CALLED -- NONE
%*** TOOLBOXES NEEDED -- NONE
%
%*** NOTES
%
% Desired number of weights, a.  Includes central weight plus weights on both sides.
%    (e.g., n==3  goes with {.25 .50 .25}).  In Panofsky reference, weights numbered 
%    0,1,2,...N.  Thus N==4 means 5 weights (n==5). Because of truncation (see below),
%    number of weights in returned filter b may be fewer than specified a%
%
%  Any weight smaller than 5% of maximum weight is dropped
%


if kopt==2;  % input arg was number of total weights in desired filter
   n=a;
   N=n-1; % minus the central weight, should be even
   if rem(N,2)~=0 || n<3;
      error('Number of weights n must be odd and greater than one');
   end;
   
elseif kopt==1; % input arg was desired wavelength (yr) of 50% response
   % Six times std deviaton of binom distrib should equal p50, period of 50% resp
   % sigma*6 == a
   % And for binomial, sigma == sqrt(nn/2)
   p50=a;
   %sigma = p50/6;  % standard deviation
   %nn =  2 * sigma .^2;
   nn = (p50/3).^2;
   
   
   % nn must be even so that with central weight the total number of weights is odd;  round computed
   % nn up to nearest integer, and then increase by one if odd
   nnpos = ceil(nn);
   if rem(nnpos,2)~=0;
       nnpos=nnpos+1;
   end;
   N =  nnpos;
end;

b=repmat(NaN,1,(N+1));

top1=factorial(N);
for m = 0:N;
   bot1=factorial(m);
   bot2=factorial(N-m);
   b(m+1)=top1/(bot1*bot2);
end;

% trim off weights smaller than 5% of central
bmax=max(b);
bmin=min(b);
Lkill = b<0.05 * bmax;
b(Lkill)=[];

bsum=sum(b);
b = b/bsum;
