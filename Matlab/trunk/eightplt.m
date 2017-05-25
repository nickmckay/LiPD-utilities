function eightplt(datin)
% eightplt: Plot up to eight plotes of ring width per page; utility called by grplot.m
% eightplt(datin);
% Last revised 2009-9-28
%
% Plot up to eight plotes of ring width per page; utility called by
% grplot.m. You will not typically call eightplt yourself.
% 
%
%*** IN 
% datin{} -- contents described later
%
%***  OUT
% No output args 
%
%
%*** REFERENCES -- none
%
%*** UW FUNCTIONS CALLED -- none
%
%*** TOOLBOXES NEEDED -- none
%
%*** NOTES
%
% This is a utility function called by grplot.m.  User should not need to call
% eightplt.m by itself, and so has no need for detailed description of input.

% unload datin{}
nwindow=datin{1}; % (1 x 2)i If not a zoomed plot, 
%   figure window for this page of plots, and total
%   number of pages (e.g., [ 1 4]  means page 1 of 4);  If a zoomed window, 
%   nwindow(1) is the window for the zoomed plots and nwindow(2) is the
%   window that was zoomed
X=datin{2}; % (? x 1)d strung-out vector of ring widths
nms=datin{3}; % (? x ?)ch names of all cores in X
yrs=datin{4}; % (? x 3)i first year, last year, and starting row index of all ringwidth 
%  series in X, in same order as nms;
iselect=datin{5}; % (? x 1)i row-index to nms of series to be plotted on this page
tbracket=datin{6}; % (1 x 2)d  specified first and last year for plot (as in zooming),
%   or [], which means figure must cover 
flmat=datin{7}; % (1 x ?)ch  name of .mat file from which ring widths come 
%   (e.g., 'shr.mat') 


% Truncate any trailing NaN off iselect
Loff = isnan(iselect);
if any(Loff);
   iselect(Loff)=[];
end;

% Compute number of series for page
nser=  length(iselect);
if nser>8;
   error('nser must be 8 or fewer');
end

% Cull rows of names and years matrices
nms = nms(iselect,:);
yrs = yrs(iselect,:);
% Now nms and yrs have series in order as to be plotted

% Compute earliest start year and latest end year of series to be plotted
yrfirst = min(yrs(:,1));
yrlast = max(yrs(:,2));

% Compute bounding decades and centuries for x axis
if isempty(tbracket); %plotting full series
   xdecade = [10*floor(yrfirst/10)  10*ceil(yrlast/10)];
   xcentury = [100*floor(yrfirst/100) 100*ceil(yrlast/100)];
   ton=[]; toff=[];
   zoomy='No';
else; % plotting a zoomed section
   ton=round(tbracket(1)); toff=round(tbracket(2));
   xdecade = [10*floor(ton/10) 10*ceil(toff/10)];
   xcentury = [100*floor(ton/100)  100*ceil(toff/100)];
   zoomy='Yes';
end

%---  Adjustments to allow for some series having no data in a zoom window
if strcmp(zoomy,'No'); % no zooming, no need to adjust
elseif strcmp(zoomy,'Yes'); % this is a zoom window, check for problems
   L1=yrs(:,1)>toff | yrs(:,2)<ton; % series ends before zoom per or starts after
   if any(L1); % some series does not exist in the zoom period
      % Lop off rows corresponding to the no-data series
      yrs(L1,:)=[];
      nms(L1,:)=[];
      iselect(L1)=[];
      if isempty(nms); % Fools might zoom where no series have data
         error('No series have data in zoom window');
      end
      % Update earliest start year and latest end year of series to be plotted
      yrfirst = min(yrs(:,1));
      yrlast = max(yrs(:,2));
      % Update number of series to plot on the zoom window
      nser = size(nms,1);
   end;
end; % if strcmp(zoomy,'No')
 
% Preliminary computations and settings 
yht = 0.1;  % height of each plot, relative units
xLL  = 0.01;  yLL=0.01;  % lower left x and y coordinates of first plot
ypos = 0.07;  % initialize y position (relative units) of sub-plots
ha = repmat(NaN,nser,1); % handles to individual plots -- allocate

% Open figure window
figure(nwindow(1));
set(gcf,'Units','normal','Position',[xLL yLL,0.85,0.85]);

% Loop over the nser series
for n = 1:nser;
   name1 = nms(n,:); % name of series
   years = yrs(n,:);  % first year, last year, starting row index in X
   iseq = iselect(n);  % sequence number within original nms and yrs of this series
   
   if strcmp(zoomy,'No'); % not a zoomed section
      % Pull the full series
      igo1=years(3);  % starting row index in X
      yrgo1 = years(1); yrsp1=years(2); % start and end year
      nyr1 = yrsp1-yrgo1+1; % number of years
      isp1 = igo1 + nyr1 - 1; % ending row index in X
      yr = (yrgo1:yrsp1)'; % year vector
      x = X(igo1:isp1); % ring-width series
   elseif strcmp(zoomy,'Yes'); % a zoomed section
      igo1=max(years(3),years(3)+ton-years(1));
      yrgo1=max(ton,years(1));  yrsp1=min(years(2),toff);
      nyr1 = yrsp1-yrgo1+1;
      isp1 = igo1 + nyr1 -1;
      yr = (yrgo1:yrsp1)';
      x = X(igo1:isp1);
   else;
      error('zoomy must be Yes or No');
   end; % if strcmp(zoom,'No')
   
   % Maximum and minimum y-value of series in plot
   yhi = max(x);  ylo=min(x);
     
   % Draw the plot axes
   ha(n)=axes('Position',[0.1,ypos,0.8,yht]);  
   
   % Make plot
   plot(yr,x,'b');
   
   % Compute y-axis limits
   yaxlim=[floor(ylo);ceil(yhi)];  
   
   % Set the X and Y axis limits and take of all axis drawings
   if strcmp(zoomy,'No'); % not a zoomed plot
      set(gca,'Xlim',xcentury,'Ylim',yaxlim,'Box','off','Ytick',[]);
   elseif strcmp(zoomy,'Yes');
      set(gca,'XLim',xdecade,'Ylim',yaxlim,'Box','off','Ytick',[]);
   end
      
   set(gca,'XGrid','on'); % add verticle tick lines
   % Label x ticks only for lowermost plot on the page
   if n~=1;
      set(gca,'Xticklabel',[]);
   end;
    
   
   % Annotate with core name at right
   text('Units','normalized','Position',[0.85,0.7],'String',[int2str(iseq),...
         ' - ',name1],'Fontsize',10);    
   % Annotate range of ring-width 
   text('Units','normalized','Position',[0.1,0.85],'String',[num2str(ylo),...
         ' - ',num2str(yhi)],'Fontsize',10);  
   
   % Add title, if top plot
   tit2=['RINGWIDTH FILE: ' flmat];
   if n==nser;
      if strcmp(zoomy,'No');
         tit1 = ['  (' int2str(nwindow(1)) ' of ' int2str(nwindow(2)) ')'];
         title([tit2 tit1]);
      elseif strcmp(zoomy,'Yes');
         tit1=['(Zoom on Figure Window ' int2str(nwindow(2)) ')'];
         title([tit2 tit1]);
      end
   else; % n .ne. nser (not topmost axes)
   end; % if n==nser
      
   % Update y position for next axes
   ypos=ypos+0.1;	
   
end; % for n=1:nser

   
   
   
   
   
   
   











