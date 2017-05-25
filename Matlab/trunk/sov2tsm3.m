function [X,yrX,nms]=sov2tsm3(v,YRS,nms,jpick,tends)
% sov2tsm: strung-out-vector to time series matrix, with  names cell
% [X,yrX,nms]=sov2tsm3(v,YRS,nms,jpick,tends);
% Last revised 2008-4-29
%
% Strung-out-vector (SOV) to time series matrix, with  names cell.
% Low-level function to convert ring-width data previously read from an rwl
% file into MATLAB by rwlinp in to a time series matrix. This function
% called by rwl2tsm. 
%
%*** IN
%
% v (mv x 1)r strung-out-vector (sov) of one or more time series
% YRS(nsers x 3)i start year, end year, and starting row index of
%		each series in v, where nsers is the number of series in v
% nms (nsers x ?)s or {nsers x 1}s names of series in v 
% jpick(? x 1)i or [] index to rows of YRS specifying which series in 
%		v to include in the tsm.  For example, jpick=([1 3 4 7])' would pick
%		only those four series.  The series numbers correspond
%		to rows of YRS. See Notes.
% tends(1 x 2)i, or []  first last year of desired tsm X. 
%
%
%*** OUT
%
% X (mX x nX)r time series matrix, mX years and nX columns
% yrX (mX x 1)i year vector for X
% nms {size(X,2) x 1}s names of series in X
%
%*** REFERENCES --- none
%
%*** TOOLBOXES NEEDED -- none
%
%*** UW FUNCTIONS CALLED -- none
%
%*** NOTES
%
% Typical application is getting ring widths from an IRTDB into Matlab as a time series matrix.  This can be done
% with a script that calls rwl2sov.m and then sov2tsm3.m:
% 1) Use rwl2sov to read an .rwl file and store the data in a .mat file
% 2) Load the .mat file, which has variables corresponding to v, YRS, and
%    nms -- which you need as input to sov2tsm3.  In the .mat file, the
%    strung-out-vector is named X, and the years-pointer matrix is named
%    yrs. 
% 3) Set jpick and tends so that output time series matrix has desired 
%    subset of series and subset of observations
% 4) Call sov2tsm3 to get the time series matrix, with its years vector and
%    a string matrix of core ids
%
% 
% X may have include some or all the time series in v, depending on jpick. 
% jpick===[]  specifies all series
%
% X is tsm covering whose number of rows and columns depend on the time
% series in v and their lengths, as well as on jpick and tends
% 
% tends.  tends==[] means X to cover entire data period of time series in v.
% Other settings (e.g., tends == [ 1600 1999] specify the time coverage of X.
% You can set tends outside the coverage of X; then there would be some all-NaN
% leading and trailing years in X. If tends is inside the time coverage, some series in 
% v are truncated in the stored versions in X
%
% jpick.  jpick==[] specifies all series in v are to be included in X. 
%
% nms.  Acceptable forms are char array or col-cell of strings


%------------ CHECK INPUTS

if nargin~=5;
	error(['Must have 5 input args, has ' int2str(nargin)]);
end

[mv,nv]=size(v);
if ~(nv==1);
    error('v must be column vector');
end

[nsers,nX]=size(YRS);
if nX~=3,
	error('Col size of YRS should be 3');
end

if ~(isa(nms,'char') || isa(nms,'cell'));
    error('nms neither char nor cell');
end;
if isa(nms,'char');
    nms=cellstr(nms); % convert nms to cell
end

if isempty(jpick)
else
    if size(jpick,2)~=1;
        error('jpick not cv');
    end
    if any(jpick<1 | any(jpick>nsers));
        error('jpick must be in range 1-nsers');
    end;
end

if isempty(tends);
else
    [mtemp,ntemp]=size(tends);
    if ~(mtemp==1 && ntemp==2);
        error('tends must be rv of length 2');
    end;
end


%---  FILL A PRELIMINARY VERSION OF X WITH ALL SERIES, INCLUSIVE COVERAGE
    

% Find earliest and latest year of any series
yrgo = min(YRS(:,1));
yrsp = max(YRS(:,2));
yr=(yrgo:yrsp)';
nyrs=length(yr);

% Allocate for X
X=repmat(NaN,nyrs,nsers); 
yrX=yr;
for n=1:nsers;
	yron=YRS(n,1);
	yroff=YRS(n,2);
	% get start and end row index in v
	i1=YRS(n,3);
	i2=i1+(yroff-yron);
	% compute start and end row index in X
	i3 = yron - yrgo +1;
	i4= yroff-yrgo+1;
	% Get the data, and put in X
	x = v(i1:i2);
	X(i3:i4,n)=x;
end


%---- TRIM COLUMNS OF X, IF NEEDED, 

if isempty(jpick);
else
    nsers=length(jpick);
    X = X(:,jpick);
    nms = nms(jpick);
    YRS=YRS(jpick,:);

    % Update earliest and latest year of any series, and trim associated matrices
    yrgo1 = min(YRS(:,1));
    yrsp1 = max(YRS(:,2));
    L=yrX>=yrgo1 & yrX<=yrsp1;
    X=X(L,:);
    yrX=yrX(L);
    nyrs = length(yrX);
    yrgo = yrgo1;
    yrsp = yrsp1;
end


%--- TRIM OR EXPAND ROWS OF X, IF NEEDED

if isempty(tends);
else
    % Initial trim
    L=yrX>=tends(1) & yrX<=tends(2);
	X=X(L,:);
	yrX=yrX(L,:);
	nyrs=length(yrX);
    
    % Optional front-padding with NaN
    nslap=yrX(1)-tends(1); % need this many years
    if nslap>0;
        yrfront=(tends(1):(yrX(1)-1))';
        Xfront = repmat(NaN,nslap,nsers);
        X=[Xfront;X];
        yrX = [yrfront;yrX];
        nyrs=length(yrX);
    end
    % Optional end-padding
    nslap=tends(2)-yrX(end);
    if nslap>0;
        yrback=((yrX(end)+1):tends(2))';
        Xback=repmat(NaN,nslap,nsers);
        X=[X;Xback];
        yrX=[yrX; yrback];
        nyrs=length(yrX);
    end
end


%--- CHECK FOR ALL-NAN ROWS; VALID ONLY IF tends SPECIFIED RANGE OF YEARS 
% 
% if kT==0; % did not specify;
%     L1 = (all(isnan(X')))'; %cv , 1 if  a row is all NaN
%     d = repmat(1,nyrs,1); %
%     d(L1)=NaN;
%     yrd=yr;
%     [x1,yrx1]=trimnan(d,yrd);
%     L2=yr>=yrgo & yr<=yrsp;
%     X(L2,:)=[];
%     yr(L2)=[];
% end
