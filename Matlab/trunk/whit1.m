function [e,k1,vrat,arcs] = whit1(y,nhi,k2)
% whit1:  fit AR model to a time series using modified AIC criterion, returning model information and residuals
% [e,k1,vrat,arcs] = whit1(y,nhi,k2);
% Last revised 2008-4-29
%
% Fit AR model to a time series using modified AIC criterion, returning model information and residuals
% You specify the highest order AR model to consider.  Models up to that order are
% fit, and the modified (small sample) Akaike Information Criterion (AIC) is used to pick the best model.
%
%*** IN **********************
%
% y (my x 1)r  time series, vector; NaNs not allowed
% nhi (1 x 1)i  highest AR order to consider (if k2==1), or the only
%   AR order model to try fitting (if k2=2)
% k2 (1 x 2)i  options
%   k2(1) for order selections
%       ==1 fit models of order 1 to nhi
%       ==2 fit model of order nhi only
%   k2(2) for over-riding selection of null (order = 0) model
%       ==1 if modified AIC computed from original time series with model order 0 is lower than 
%           any of the entertained models, return the null model (see notes)
%       ==2 accept the lowest AIC model even if its AIC is not as low as that of the null model
%
%*** OUT **************************
%
%  e (my x 1)r AR residuals, with mean added back in; or, if null model, the
%		original series y
%  k1 - the order of the AR model deemed best by the AIC, or 0 if null model and k2(2)==1
%  vrat - the ratio of variance of AR residuals to variance of original time series y (see notes)
%  arcs the ar coefs and their two-standard errors in a two-row array; row 1 has
%       the coefficients; row two has 2*standard error of the coefficients; 
%       arcs==[] if k2==1 and null model has been selected; 
%
%*** REFERENCES
% 
% Ljung, L. 1995. System identification toolbox; for use with MATLAB, The 
% MathWorks, Inc., p. 3-46
%
% Akaike H. (1974) A new look at the statistical model identification. IEEE Trans. Autom. Control AC-19, 716-723.
%
% Hurvich C. M. and Tsai C. (1989) Regression and time series model selection in small samples. Biometrika 76, 297-307.
%
% 
%*** UW FUNCTIONS CALLED 
%
% akaike
%
%
%*** TOOLBOXES NEEDED: ident
%
%*** NOTES
%
% vrat: the variance ratio is computed over years k1+1 to n1, where n1 is length of y
%
% null model (k1==0): 
% The "Loss function" V is the normalized sos of prediction errors, or the 
% variance of the AR residuals.
% A "null model" loss function is defined as the mean sos of the
% variable z (original data with mean subtracted) over the years nhi+1 to the
% last year of z.  If the null-model loss function is no higher than the V
% for any estimated model, a "null model" is assumed.  This means no AR model is
% justified, and k1==1 is returned.
%
% Revised 2005-8-28:  Revised to call function akaike for the AIC adjusted for small sample size as defined by Hurvich C. M. 
% and Tsai C. (1989); BUT deactivated this change because NEVER indicated needed higher than order 1
% 
% For fair comparison of models, only the residuals from observations beginning with nhi are used for
% comparison of models.  Thus, for example, if a time series of length 100 years is modeled and orders 1-6 are
% entertained, the residuals for observations 7-100 are used for computing the AIC.  
% 
% vrat: the ratio is computed only on obervations beginning with obervation k1+1, where k1 is the final
% selected order of AR model
% 

L=isvector(k2) && length(k2)==2;
if ~L;
    error('k2 must be vector of length 2');
end;

mn=mean(y);
z=detrend(y,'constant');


% If nhi specified as 0, will not want to fit any models, and to return info 
% as for null model
if nhi==0;
   e=y; k1=0; vrat=1.0;  arcs=[0 0]';
   return;
end;


if k2(1)==1;   %  mode 1, fit up to order nhi
	NN=(1:nhi)';  % orders to try
else  % mode 2, fit order nhi only
	NN=nhi;
end

i1 = ((nhi+1):length(z))';  % time vector marking residuals to be used in computing variance of estimated
%       residuals for comparison of various models  


%--- Revision 2005-8-28 :  Get best model by "small sample" AIC criterion

nmods = size(NN,1); % number of models to be tried
nobs = length(z); % number of observations N for call to akaike
AIC1 = repmat(NaN,nmods,1); % to store adjusted AIC (adjusted for small sample size)
AIC2 = repmat(NaN,nmods,1); % to store unadjusted AIC
for n = 1:nmods;
    nn=NN(n); % current AR order
    th=arx(z,nn); % estimate AR model

    % Get time series of residuals
    dat2 =iddata(z,[],1);
    yhat=predict(th,dat2,1,'zero'); % one-step ahead prediction of z
    e = z-yhat.OutputData; % residuals of AR or ARMA model
    echeck = e(i1); % these resids will be used to compute AIC

    % Vthis =th.NoiseVariance;
    Vthis = var(echeck);
    c=akaike(Vthis,nobs,nn);
    AIC1(n) = c(1); % adjusted
    AIC2(n) = c(2); % unadjusted

end;

[stemp,itemp]=min(AIC1); % find model with lowest small-sample AIC
nn  = NN(itemp); % order of selected best model


%--- For later use, compute small-sample AIC of null model (AR(0))

ztrunc = z(i1);
cnull=akaike(var(ztrunc),nobs,0);
if all(cnull(1) <= AIC2);
    null_model='Yes';
else
    null_model='No';
end;


%--- Re-fit the selected  best model and store its statistics 

k1=nn; % the selected order of  best ar model
i2 = ((k1+1):length(z))';  % time vector marking residuals for selected model;  only those residuals not
% depending on data before initial observation  
th=arx(z,nn); % recompute the estimated model based on parsimonious selection
dat2 =iddata(z,[],1);
yhat=predict(th,dat2,1,'zero'); % one-step ahead prediction of z
e = z-yhat.OutputData; % residuals of AR  model
e(1:k1)=NaN; % Force the "leading" residuals to NaN


%--- Compute ratio of variance of residuals of fitted model to variance of original series
vrat= (std(e(i2)) ^2) / (std(z(i2)) ^2);

e=e+mn;

% Revision 2-16-02
thsub=get(th,'CovarianceMatrix'); % covariance matrix of estimated ar parameters
thsub=diag(thsub); % variances of the estimated parameters, as a col vector
stderr= 2*sqrt(thsub); % twice the std error of the parameters, as col vector
arcs=get(th,'a'); % ar coefs, with leading '1', as row vector
if arcs(1)==1;
    arcs(1)=[];
else
    error('Leading value in th.da not 1');
end;
arcs=[arcs; stderr']; % ar coefs in row 1, 2Xstderr in row 2


%--- OPTIONALLY RETURN THE NULL MODEL WHEN SMALL-SAMPLE AIC  OF A NULL MODEL (ORDER 0, ORIGINAL DATA
% USED AS RESIDUALS) IS LESS THAN ANY OF THE ENTERTAINED AR MODELS.  

if k2(2)==1;
    if strcmp(null_model,'Yes');   %  AIC1 for null model is smaller than for
        % any other model, so do not whiten.  Pass the orig
        % series back as the "whitened" series, and tell
        % that model is null

        k1=0;
        e=y;
        vrat=1.0;
        arcs=[0 0]';
    end
else
end;


