function [mpcp,npcp,mtmp,ntmp]=climgram(P,T,txtin,windno,koptcolor)
% climgram: box-plot graphs showing monthly distributions of precipitation and temperature
% [mpcp,npcp,mtmp,ntmp]=climgram(P,T,txtin,windno,koptcolor);
% Last revised 2009-10-04
%
% Box-plot graphs showing monthly distributions of precipitation and temperature.
% A figure with two panels, each having 12 box plots, is drawn.  The top plot 
% shows the distribution of monthly precipitation; the bottom plot shows the 
% distribution of monthly temperature.  The plots convey the same information
% as the conventional "climatogram", or "climograph", but dislay the variability as
% well as the mean level of the monthly climate variables.  
%
%*** IN 
%
% P (? x 13)r  monthly precipitation matrix, year in col 1
% T (? x 13)r  monthly temperature matrix, year in col 1
% txtin{} -- Labeling for plots
%   {1} (1 x ?)s title for plot (will go above top plot). Say,
%       'Climatogram for Rapid City'
%   {2} (1 x ?)s y axis label for pcp  Example
%      'Precipitation (mm)'
%   {3} (1 x ?)s y axis label for tmp
% windno: window number for plot
% koptcolor (1x1)i  color option
%   ==1 color
%   ==2 B/W
%
%*** OUT
%
% mpcp (1 x 12)r  means for pcp
% npcp (1 x 12)n  number of years in sample
% mtmp (1 x 12)r  means for tmp
% ntmp (1 x 12)n  number of years in sample
%
%
%*** REFERENCES -- NONE
%
%*** UW FUNCTIONS CALLED --NONE
%
%*** TOOLBOXES NEEDED
% stats
%
%*** NOTES
%
% Makes two axes in a figure window.  Top axes is boxplot distribution of monthly
% precip.  Bottom axes is for monthly temperature, which might be monthly means of
% daily means, daily maximums, or whatever.  
%
% The two climate variables may be other than precipiation and temperature.
% Labeling is controled through one of the input arguments.  Just be sure
% the labeling matches the data
%
% Input argument windno allows was included so that climgram could be
% called from a calling script or function and not overwrite some figure
% window that you want preserved


%------ CHECK INPUT

[mtemp,ntemp]=size(P);
if ntemp~=13;
   error('P must have 13 cols');
end
[mtemp,ntemp]=size(T);
if ntemp~=13;
   error('T must have 13 cols');
end

L = iscell(txtin) && isvector(txtin) && (length(txtin))==3;
if ~L;
    error('txtin must be cell-vector of length 3');
end

if ~isscalar(koptcolor);
    error('koptcolor must be scalar');
end
if ~any(koptcolor==[1 2]);
    error('koptcolor must be 1 or 2');
end


%------ Compute mean of monthly precip, using only valid data
P1 = P(:,2:13);
npcp = sum(~isnan(P1));
mpcp = nanmean(P1);

%------ Compute mean of monthly temperature, using only valid data
T1 = T(:,2:13);
ntmp = sum(~isnan(T1));
mtmp = nanmean(T1);

%************ FIGURE
% Sample Caption
% Figure .  Graphs showing distributions of monthly climatic variables at
% Great Sand Dunes.  Top: monthly total precipitation.  Bottom: monthly averaged
% daily maximum temperature.  Boxplots based on data from Great Sand Dunes National 
% Monument. Each box summarizes distribution of 47 values (1951-97). Boxplot 
% elements are median (horizontal line in middle of box); interquartile range 
% (extents of box); adjacent values (whiskers), defined as the most extreme values
% still within 1.5 times the interquartile range of the edges of the box; and 
% outliers (+) -- values greater than that distance from the edges of the box. 
% Boxplot definitions from Cleaveland (1993). 


% If the desired figure window exists, get rid of it
jwindows = get(0,'Children');
if ~isempty(jwindows)
    if any(jwindows==windno);
        close(windno);
    else
    end
end



figure(windno);
set(gcf,'DefaultLineLineWidth',1.5);
xtlab = {'J','F','M','A','M','J','J','A','S','O','N','D'};

hax1=axes('Position',[.1 .1 .8 .4]);
hax2=axes('Position',[.1 .55 .8 .4]);

if koptcolor==1; % color
    symb1='r+'; % outliers
else
    symb1='k.'; % outliers
end


%************* TMP

boxplot(hax1,T1,'Symbol',symb1);
if koptcolor==2;
    h=findobj(gca,'tag','Median');
    for n = 1:length(h);
        hthis =h(n);
        set(hthis,'Color',[0 0 0]);
    end
    h=findobj(gca,'tag','Box');
    for n = 1:length(h);
        hthis =h(n);
        set(hthis,'Color',[0 0 0]);
    end
end
set(hax1,'XTickLabel',[]);
set(hax1,'Xtick',(1:12),'XTickLabel',xtlab);
set(hax1,'Fontsize',11);

ylabel(hax1,txtin{3},'FontSize',14);
xlabel(' ');



%************* PCP
boxplot(hax2,P1,'Symbol',symb1);
if koptcolor==2;
    h=findobj(gca,'tag','Median');
    for n = 1:length(h);
        hthis =h(n);
        set(hthis,'Color',[0 0 0]);
    end
    h=findobj(gca,'tag','Box');
    for n = 1:length(h);
        hthis =h(n);
        set(hthis,'Color',[0 0 0]);
    end
end
set(hax2,'XTickLabel',[]);
set(hax2,'Xtick',(1:12),'XTickLabel',' ');

set(hax2,'Fontsize',11);

ylabel(hax2,txtin{2},'FontSize',14);
xlabel(' ');
title(txtin{1});
