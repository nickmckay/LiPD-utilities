function textcorn(txt,pos,xoffset,yoffset,fsz)
% textcorn: Add annotation text to any corner of a figure
% textcorn(txt,pos,xoffset,yoffset,fsz);
% Last Revised 2009-10-05
%
% Add annotation text to any corner of a figure.
% Control over which corner, how far from axes, and font size. One common
% use is to label subplots as "A", "B", etc.
%
%
%*** INPUT 
%
% txt (1 x ?)s or {}s =  text of label
% pos (1 x 2)s position (one of these: "UL","UR","LL" or "LR")
% xoffset (1 x 1)r how far text is from left or right axis, as percentage
%   of XLim axis property
% yoffset (1 x 1)r how far text is from bottom or top axis, as percentage
%   of YLim axis property
% fsz (1 x 1)i font size
%
%*** OUTPUT
%
% No output, just puts text on the figure
%      
%
%*** REFERENCES --- none
%
%*** UW FUNCTIONS CALLED -- none
%
%*** TOOLBOXES NEEDED -- none
%
%
%*** NOTES
%
% Examples of use:
%
% textcorn('A','UL',.02,.02,20); % Puts text label "A" at upper left
%   of figure.  UL will be left justified.  xoffset of 0.02 means start
%   2% of the way from the left vertical axis.  yoffset of 0.02 means start
%   2% of the way down from the top.
%
% txt ={['Mean=' num2str(xmean,'%5.2f],['Median=' num2str(xmed,'%5.2f]
% textcorn(txt,'UR',.02,.02,20); % Puts text in cell "txt" at upper right
%   of figure.  UR will be right justified.  xoffset of 0.02 means start
%   2% of the way from the right vertical axis.  yoffset of 0.02 means start
%   2% of the way down from the top.


xlims = get(gca,'XLim');
ylims = get(gca,'YLim');

switch pos
    case 'UL';
        xpt = xlims(1)+xoffset*diff(xlims);
        ypt = ylims(2)-yoffset*diff(ylims);
        htext = text(xpt,ypt,txt,'HorizontalAlignment','Left','VerticalAlignment','Top','FontSize',fsz);
    case 'LL';
        xpt = xlims(1)+xoffset*diff(xlims);
        ypt = ylims(1)+yoffset*diff(ylims);
        htext = text(xpt,ypt,txt,'HorizontalAlignment','Left','VerticalAlignment','Bottom','FontSize',fsz);
    case 'UR';
        xpt = xlims(2)-xoffset*diff(xlims);
        ypt = ylims(2)-yoffset*diff(ylims);
        htext = text(xpt,ypt,txt,'HorizontalAlignment','Right','VerticalAlignment','Top','FontSize',fsz);
    case 'LR';
        xpt = xlims(2)-xoffset*diff(xlims);
        ypt = ylims(1)+yoffset*diff(ylims);
        htext = text(xpt,ypt,txt,'HorizontalAlignment','Right','VerticalAlignment','Bottom','FontSize',fsz);
    otherwise
        error('Wrong pos selection');
end


