function [cL,cB,cW,cH]=figsize(fwidth,fheight)
% figsize: figure-window pixel positions from specified fractional screen-width and screen-height
% [cL,cB,cW,cH]=figsize(fwidth,fheigth);
% Last Revised 2009-10-04
%
% Figure-window pixel positions from specified fractional screen-width and screen-height.
% You want to set position property of figure window such that figure window
% covers a specified fraction of screen regardless of how many pixels
% are in the x and y directions on your computer.
%
%*** INPUT 
%
% fwidth (1 x 1)r   desired figure width as decimal fraction of screen width
% fheight (1 x 1)r  desired figure height as decimal fraction of screen height
%
%*** OUTPUT
%
% cL (1 x 1)i  left position as pixel
% cW (1 x 1)i  width in pixels
% cB (1 x 1)i  bottom position as pixel
% cH (1 x 1)i  height in pixelsesult -- structure of results
%
%*** REFERENCES --- none
%
%
%*** UW FUNCTIONS CALLED -- none
%
%*** TOOLBOXES NEEDED -- none
%
%*** NOTES
% 
% In calling program, call figsize, then to resize figure window use:
% set(gcf,'Position',[cL cB cW cH])
%
% In calling program, the following is example of application
% [cL,cB,cW,cH]=figsize(.5,.4);
% set(gcf,'Position',[cL cB cW cH]);
%
% In sizing figure for an eps output, you would also give these commands:
% set(gcf,'PaperPositionMode','Auto');
% eval(['print -depsc2 dufus_F1']);




Ssz=get(0,'screensize'); % Get screen size

%---CHECK INPUT

if nargin~=2;
    error('Number on input args should be 2');
end
L=[isscalar(fwidth) isscalar(fheight)];
if ~all(L);
    error('fwidth and fheight must be scalars');
end
L=[isnumeric(fwidth) isnumeric(fheight)];
if ~all(L);
    error('fwidth and fheight must be numeric');
end

if fwidth<0.1 | fwidth>0.9;
    error('Width as fraction of screen width must be between 0.1 and 0.9');
end;
if fheight<0.1 | fheight>0.9;
    error('Height as fraction of screen height must be between 0.1 and 0.9');
end;


%--- Compute required number of pixels in x and y directions

cW=floor(fwidth*(Ssz(3)-Ssz(1))); % need this many pixels for width
cH =floor(fheight*(Ssz(4)-Ssz(2))); % need this many pixels for heigth
wcarcass = Ssz(3)-cW; % this many pixels width left after alloting for figure
hcarcass = Ssz(4)-cH; % this many pixels height left after alloting for figure
cL = floor(0.5* wcarcass);
cB = floor(0.5* hcarcass);


if (cL+cW)>=Ssz(3);
    error('Screen width cannot accomodate specified position');
end;
if (cB+cH)>=Ssz(4);
    error('Screen height cannot accomodate specified position');
end;

