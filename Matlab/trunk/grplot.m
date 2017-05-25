function grplot
% grplot: stacked time series plots of ring-width series from rwl file 
% grplot;
% Last revised 2008-5-2
%
% Stacked time series plots of ring-width series from rwl file. Up to 8 series
% plotted per figure windowm, or printed page. Intended to help in deciding on curve-fits 
% for detrending in programs such as ARSTAN.  Can process single rwl file (interactive 
% mode), or multiple rlw files(batch mode). Series can be plotted in order as encountered
% in the rwl file, or re-ordered by age. Series for each page can also be specified if
% user first stores a pointer variable in a .mat file beforehand. 
%
%*** IN 
%
% No input arguments
%
% User prompted for various options, and to point to files for input and
% output
%
%*** OUT 
%
% No output args.
%
% Plots of time series appear in one or more figure windows. 
%
% If your input ring-width data is from an .rwl file(s), an ascii .txt file with name 
% xxx_list.txt appears in the working directory.  "xxx" is the part of the
% rwl filename before the period.  Thus, if "az024.rwl" is your input,
% "az024_list.txt" is produced.  This .txt file is for surveying file
% contents and lists each core id and first and last years' measurments 
%
% Other file output is optional, and consists of one or more postscript (.ps) files, one for
% each input .mat ring-width file.  The user can specify the filename in interactive
% mode.  In batch mode, the .ps suffix is assigned to the same prefix as the input
% .mat file containing the ring-width file.
%
% In "single" mode you can view the figure windows as the program runs and afterwards.
% In "batch" mode, figure windows are not saved, but are overwritten from on
% ring-width file to ring-width file.  But in batch mode, have the plots stored in
% .ps files for later plotting.
%
%*** REFERENCES -- none
%
%*** UW FUNCTIONS CALLED 
%
% eightplt - utility function that plots up to 8 sets of axes on page
% rwlinp - read rwl file; store data as indexed vector (strung-out-vector) and metadata 
% trailnan --- misc utility
%
%*** TOOLBOXES NEEDED -- none
%
%*** NOTES 
%
% grplot plots "groups" of ring-width series, several to a page. 
% Up to eight series can be plotted per page.  Annotated at left of each plot
% is the range of ring widths in hundredths of mm (e.g., "2-300" means the smallest and
% largest ring widths are .02 mm and 3.00 mm.  Annotated at right is the sequential
% number of the core ring-width series in the source .rwl file, and the core id.
% The user can control which series are plotted and in what order. The default is in
% order as the series are stored in the original .rwl file. A useful option is to select
% ordering by start year of the series.  Ring widths can be read from either an .rwl file
% or a .mat file.  The .mat file option requires the data be a "strung-out-vector" stored
% previously by function rwlinp.m <P>
%
% The intended use of grplot is as an aid in deciding on the form of the
% growth curve to use in ARSTAN or other standarization programs.
% Low-frequency ring-width fluctuations not shared by different trees can be spotted
% in the plots. If the chronology is supposed to track climate variations,
% it's usually a good idea to select detrending curves that remove such low-frequency
% fluctuations. <P>
%
% grplot can optionally be run in two modes:  "single" or "batch".  Single mode
% applies to a set of ring-width series from one site.  Single mode is most
% interactive (with zoom options) and is the most likely mode. Batch mode applies to
% multiple files of ring-width series, perhaps from several sites. Batch mode is
% not interactive, but is useful if you have to plot series from many sites.  In
% batch mode, .ps files, one per site, for later printing and viewing.
% How to send .ps files to the printer is system-dependent -- see your
% system instructions. 
%
%
% Modes:
%
% One mode is "single" for a single site with ring widths stored in .rwl file
% or .mat file.  In this mode, user is prompted to click on the input file.
% If a .rwl file, it should be formatted as conventional with the ITRDB. If
% a .mat file, you should have made it with rwlinp.
%
% Other mode, rarely likely to be used, is "batch", in which the user points to 
% and ascii .txt file that contains filenames (.rwl or .mat) for multiple sites
% These files are processed in sequence, and postscript printer files of figure windows
% are produced, one postscript file for each site.
%
% In either mode, series can be plotted in order as they are stored in the .rwl or
% .mat file, or can be re-ordered in one of two ways:
%  1) from oldest to youngest
%  2) arbitrarily, as indicated by an optional pointer variable.  The pointer variable
%    is stored in a separate .mat file that the user is prompted to click on.
%
% Plots are annotated with core id and with minimum and maximum ring width
% (hundredths of mm) in the plot window.  These annotated values are critical because
% each plot on the figure is scaled differently on the y-axis.  Each series takes up
% the same proportion of the y-axis, and the differential scaling adjusts for differences
% in absolute growth rates.  y-axis tick marks are not labeled.
%
% Requirements for input files:
%   .rwl file: International Tree-Ring Data Bank (ITRDB) compatible
%   .mat ring-width file:  contains the variables nms, yrs, X, as created
%       by rwlinp.m
%   .mat pointer file <optional>: contains a row-cell variable Vselect that specifies which
%       series are to be plotted on each page, and in what order.  Vselect should be a row-cell
%       of row-cells, with the elements of the bottom-level row-cells being numeric vectors. The
%       vectors specify the series numbers, with a sequential number as the series is ordered in
%       the rwl or mat file.  Series are plotted in order as specified from bottom to top of page.
%       This is best explained by example.  Say you have a single rwl file, and want two figure
%       windows, with series [7 3 1] on Fig 1 and series [12 11 10 5 6] on Fig 2.  You would save 
%       a variable Vselect={{[7 3 1],[12 11 10 5 6]}} in a .mat file, say "pointer1.mat". Then when
%       prompted for the pointer file you would click on it, and see Figure 1 with series 7 at the 
%       bottom, series 3 above it and series 1 above that; and Figure 2 with series [12 11 10 5 6]
%       ordered from bottom to top.
%
%       If you happened to be running batch mode, with two rwl files, your point file might have
%       a Vselect something like this:
%       Vselect={{[7 3 1],[12 11 10 5 6]},{[3 2 1],[7 9 10]}};
%       Here the series to be plotted for the second file are given by {[3 2 1],[7 9 10]}
%
%
% QUICK OPERATING INSTRUCTIONS -- SIMPLE CASE: SINGE RWL FILE, PLOT ALL
% SERIES, ARRANGED ON PAGES IN ORDER OF START YEAR
%
% Start matlab
% Make sure the desired rwl file, "az026.rwl"  is in your current working directory
% grplot
% "rwl" as input file type
% "No" for batch mode
% "No" for use pointer
% "Yes: for arrange in order of age
% Select "az026.rwl" in the file window
%    Figure windows are produced;  menu is stilll active
% "Quit zooming"  at the zoom menu
% "No" for make a postscript file
% "No" for close the figure windows
% 
% You now see the figure windows, and can view and print them as desired.
% You also see a file called az026_list.txt in your current directory; this
%    lists the series, and their first and last years
%
%
%  VARIATION -- ZOOMED FIGURE
%
% "Zoom a figure" from menu when the choice appears
% Click the desired figure number on the menu
% At the prompt, use you pointer to click at a left (early)
%    and right (late)point on a figure-- The series zooms to
%    include only that portion
% Not happy with that zoom?  Click zoom a figure again, and
%    choose the same figure, with different portion. 
% "Quit Zooming" when happy, then proceed as before closing out
%
%
% VARIATION -- SPECIFIED SERIES/ORDER ON FIGURES
%
% Say you have looked at az026_list and decided you wanted figure 1 with
% series 1 3 5, ordered from bottom of plot, and figure 2 with series 2 4 6
% from bottom of plot
% 
% In Matlab, same directory as the .rwl file, give this command
%   Vselect = {{[1 3 5],[2 4 6]}}
%   save pointer_1 Vselect
% grplot
% "rwl" as input file type
% "No" for batch mode
% "Yes" for use pointer
% Select "pointer_1" from file window as your input file with selection pointer, at prompt
% "No": for arrange in order of age
% Select "az026.rwl" in the file window
%    Figure windows are produced;  menu is stilll active
% "Quit zooming"  at the zoom menu
% "No" for make a postscript file
% "No" for close the figure windows
% 
% You now see the figure windows, and can view and print them as desired.
% You also see a file called az026_list.txt in your current directory; this
%    lists the series, and their first and last years
%    
%
% VARIATIONS -- BATCH MODE, WANT PS FILES WITH  PLOTS FOR  az026, az027, az037
%
% With text editor, make ascii file myfiles.txt file with 3 lines, left
% justified; save that in current directory, and make sure all 3 files are
% there
%    az026.rwl
%    az027.rwl
%    az036.rwl
%
% grplot
% "rwl" as input file type
% "Yes" for batch mode
% At file menu, click on "myfiles.txt" as the infile with list of rwl or mat filenames
% Click OK on the window that comes up asking if you want to store the ps files in your 
% 	current directory
% "No" for use pointer
% "Yes": for arrange in order of age
% You see the windows flash by for each rwl file; these are closes automatically
% You now see postscript files az026.ps, az027.ps, az036.ps in current directory
% Ask your system administrator how to send those postscript files to a printer
%    (it can be automated so that the whole bunch can be sent at once)



% Close any open figure window
close all;

% Get current directory path
pathcurr=[eval('cd') '\'];


%---- Prompt for form of input file with ring widths

filetypes={'.rwl','.mat'};
kmen2=menu('Choose the type of file for input ring-width data',filetypes);
if kmen2==1;
    filesuff='rwl';
else
    filesuff='mat';
end


%--- BATCH MODE OR INTERACTIVE MODE

btchmode=questdlg('Batch mode (requires a .txt filelist)?');
switch btchmode;
    case 'No';
        % no action needed
    case 'Cancel';
        return
        % no action needed;
    case 'Yes';
        [file3,path3]=uigetfile('*.txt','Input .txt file with list of .rwl or .mat filenames');
        pf3=[path3 file3];
        if ~(exist(pf3,'file')==2);
            error(['Claimed file ' pf3 ' with list of .rwl or .mat filenames does not exist']);
        end
        % Prompt for directory you want the .ps files to go into
        prompt={'Enter path to store ps files:'};
        def={pathcurr};
        dlgTitle='Directory to store postcript (.ps) output files in';
        lineNo=1;
        answer=inputdlg(prompt,dlgTitle,lineNo,def);
        pathps=answer{1};
 
end; % switch
% btchmode == 'Yes' means use batch mode
% pf3 would be the .txt filelist file if in batch mode


%--- Compute number of ring-width files to treat in this run

if strcmp(btchmode,'No') ; % using 'single' mode
    nfiles=1; % number of .mat ring-width files
    filecell=[]; % row-cell holding names of the .mat files
else % batch mode
    filecell = textread(pf3,'%s','delimiter','\n','whitespace','');
    nfiles=size(filecell,1); % number of .mat files to read
end; % strcmp(btchmode...)
% filecell is a row-cell with names of the .mat files
% nfiles is the number of .mat files


%--- Plot all series in each file, or use a pointer to select files?

pointopt=questdlg('Use pointer to select ring-width series?');
switch pointopt;
    case 'No'
        % no action needed
        
    case 'Cancel';
        return
    case 'Yes';
        % load file with pointer variable;
        [file5,path5]=uigetfile('*.mat','Input file with selection pointer');
        pf5=[path5 file5];
        eval(['load ' pf5 ' Vselect;']); % pointer variable
        if exist('Vselect','var')~=1;
            error(['File ' pf5 ' does not contain Vselect']);
        end
        % Check size of Vselect
        if ~iscell(Vselect);
            error('Vselect must be a cell variable');
        end
        ncheck=length(Vselect);
        if ncheck~=nfiles;
            error('Vselect length not equal to nfiles');
        end
        clear  ncheck ;

end; % switch
% pointopt is 'Yes' if using a  pointer file
% If using a pointer file, Vselect is a rv or matrix of pointers to ring-width series

%------ Prompt for optional re-ordering of cores in .mat file from oldest to youngest for plotting
oldfirst= questdlg('Arrange cores in order of age in plots?');
switch oldfirst;
    case 'Cancel';
        return;
    otherwise
end
%  If pointopt=='yes', the ordering is within rows of Vmtx, which means
%  that retain the restriction that a specified group of cores is plotted
%  in each window
% If pointopt ~='yes', the ordering is over all cores in the .mat file
% Actual re-ordering is done within eightplt.m

%------ Loop over .mat files
for n = 1:nfiles;
    
    %-----  Get the ring-width input filename
    if ~strcmp(btchmode,'Yes'); % single mode
        if kmen2==2;
            [flmat,path1]=uigetfile('*.mat','.MAT filename ?');
        else
            [flmat,path1]=uigetfile('*.rwl','.rwl filename ?');
        end
        pf1=[path1 flmat];
    else % batch mode -- use a .txt list of .mat filenames
        pf1=filecell{n}; % file name, with or without drive\path
        fslash=findstr(pf1,'\');
        if isempty(fslash); % no path prefix in file name; set path1 to current dir
            flmat=pf1; % filename (w/o path)
            pf1 = [pathcurr pf1];
        else % separate path and filename
            flmat=fliplr(strtok(fliplr(pf2),'\')); % filename
        end
        % If needed, put on the .rwl or .mat suffix
        suffy = ['.' filesuff];
        if isempty(findstr(pf1,'.'));
            pf1=[pf1 suffy];
            flmat=[flmat suffy];
        end

    end
    % pf1 now is complete path\filename, including .rwl or .mat
    % flmat  is the filename, with .rwl or .mat



    %----- Load the  file containing the ring-width series, names, years, etc;

    if kmen2==2; % it is .mat file
        % Check that it holds the vital variables
        eval(['load ',pf1]);
        if ~all(exist('X','var')==1 & exist('nms','var')==1 & exist('yrs','var')==1);
            error('.mat input ring-width file does not have required variables');
        end
    else % it is .rwl
        [pfdummy,X,yrs,nms]=rwlinp(pf1);
    end
    ncore=size(nms,1);  %  number of ring-width series (cores) in the file,
    %  and maybe number to be plotted (depending on pointeropt)


    %--------  Make or pull matrix of selection pointers
    if strcmp(pointopt,'Yes'); % use read-in pointer variable
        Vmtx = Vselect{n}; % row-cell; each cell has numeric rv with sequence number of series to be plotted in each fig window
        if ~iscell(Vmtx);
            error('Each cell of Vselect must itself be a cell');
        end
        numfig = length(Vmtx); % number of figure windows
        ncore=0; % initialize counter of total number of series in this file to be plotted -- summed over figure windows
        % loop over figure windows to count total number of series to be
        for jtemp = 1:numfig; % loop over figure windows to count total number of series to be plotted
            ntemp=Vmtx{jtemp};
            if ~isnumeric(ntemp) || size(ntemp,1)~=1;
                error('Cells of Vselect should themselves be cells holding NUMERIC row vectors');
            end
            ncore = ncore+length(ntemp);
        end;
        % For compatability with old code, now convert Vtmx to a numeric
        % matrix, numfig rows and 8 columns
        Vtemp = repmat(NaN,numfig,8);
        for jtemp = 1:numfig;
            vthis = Vmtx{jtemp};
            numthis = length(vthis);
            Vtemp(jtemp,1:numthis)=vthis;
        end
        Vmtx = Vtemp;
        clear jtemp ntemp Vtemp vthis numthis
    else % not using pointer option;  build matrix of core pointers
        numfig = ceil(ncore/8); % number of figure windows
        i1=1:8;
        I1=repmat(i1,numfig,1);
        j1=(0:8:ncore-1)';
        J1=repmat(j1,1,8);
        Vmtx=I1+J1;
        ntemp = 8 * numfig;
        nquash = ntemp - ncore;
        if nquash>0;
            Vmtx(numfig,(8-nquash+1):8)=NaN;
        end
    end


    %------  Order cores from oldest to youngest before plotting.
    if strcmp(oldfirst,'No'); % No re-ordering wanted
    else % re-order
        if strcmp(pointopt,'Yes'); % using pointer option to specify cores in plot windows
            for ii=1:numfig; % loop over number of figure windows
                i1 = Vmtx(ii,:); % core sequence no's for this window
                L1 = isnan(i1); % any NaN's for this window
                if any(L1);
                    nquash=sum(L1);
                    i1(L1)=[];
                    if length(i1)==1; % just one series to be plotted in window
                        Vmtx(ii,:)=[i1 repmat(NaN,1,7)];
                    else % more than one series; need to sort
                        yrborn = yrs(i1,1); % start year of rw for selected series
                        [yrtemp,isort]=sort(yrborn);
                        i2=i1(isort);
                        Vmtx(ii,:)=[i2,repmat(NaN,1,nquash)];
                    end;
                else % no NaN -- have 8 series to be plotted
                    yrborn=yrs(i1,1); % start years
                    [yrtemp,isort]=sort(yrborn);
                    Vmtx(ii,:)=i1(isort);
                end; % if any(L1)
            end; % for ii=1:numfig
        else % not using pointer option; re-order all cores in the .mat file
            i1=(1:ncore)'; % col vector of indices corresp to sequence of cores
            yrborn = yrs(:,1); % col vector of first years of ringwidths
            [yrtemp,isort]=sort(yrborn);
            i2=i1(isort);  % core seq rearranged in order of start year of series
            if nquash>0; % need to make n of plot series multiple of 8
                i2=[i2; repmat(NaN,nquash,1)];
            end
            Vmtx=(reshape(i2,8,numfig))';
        end; % strcmp(pointopt,...);
    end; % strcmp(oldfirst,...) That's it for re-ordering



    % ---- Set datin{} contents that do not vary over figure windows
    datin{2}=X; % sov of ring widths
    datin{3}=nms; % core Ids
    datin{4}=yrs; % start year, end year, start row index of ring widths
    datin{7}=flmat; % (1 x ?)ch  name of .mat file from which ring widths come
    %   (e.g., 'shr.mat')

    %-------- Loop over figure windows
    for nn = 1:numfig;
        %-------  Load up input args for call to eightplt.m
        datin{1}=[nn numfig]; % window number & number of windows (not counting zoom)
        datin{5}=Vmtx(nn,:); % (? x 1)i row-index to nms of series to be plotted on this page
        datin{6}=[]; %  (1 x 2)d  specified first and last year for plot (as in zooming),
        %   or [], which means figure must cover

        %---  Make the plots
        eightplt(datin);
    end; % for nn=1:numfig

    %------- ZOOM CAPABILITY

    if strcmp(btchmode,'Yes'); % zooming not implemented in batch mode
        % no zooming
    else % 'single' mode
        kzoom=1;
        while kzoom==1;
            kmen1=menu('Choose One',...
                'Zoom a figure window',...
                'Quit zooming');
            if kmen1==1; % zoom a figure window

                if exist('nzw','var')==1;
                    close(nzw);
                end

                nzw = numfig+1; % figure window in which to put zoomed plot
                % close any existing zoom window

                % Build menu of possible windows to zoom
                figcell= cellstr(num2str((1:numfig)'));

                % Prompt for choosing a figure window , then switch to that window
                zwind=menu('Zoom on which window?',figcell);
                figure(zwind);

                % Prompt user to point to zoom region
                helpdlg('Click L and R edge of desired zoom region');
                pause(1.5);
                xypnts=ginput(2);   % Get the corner points of the region to be zoomed in
                xmx=max(xypnts(:,1));
                xmn=min(xypnts(:,1));

                % Make zoomed plot
                %-------  Load up input args for call to eightplt.m
                datin{1}=[nzw zwind]; % zoom window & source window
                datin{5}=Vmtx(zwind,:); % (? x 1)i row-index to nms of series to be plotted on this page
                datin{6}=[xmn xmx]; %  (1 x 2)d  specified first and last year for plot (as in zooming),
                %   or [], which means figure must cover

                %---  Make the plots
                eightplt(datin);

            elseif kmen1==2; % quit zoom, but keep figures available
                kzoom=0;
            end; % if kmen1=1;
        end;  % while kzoom==1
    end; % strcmp(btchmode,...)

    %****************** OPTIONALLY MAKE POSTSCRIPT FILE OF THE FIGURE WINDOWS

    if ~strcmp(btchmode,'Yes'); % not in batch mode; optional making of .ps file
        psfile=questdlg('Make a postscript plot file?');
        switch psfile;
            case 'Yes'; %make a ps output file
                txt3=[' Output ps file for ' pf1];
                [file2,path2]=uiputfile('*.ps',txt3);
                pf2=[path2 file2];
                for npost = 1:numfig;
                    figure(npost);
                    eval(['print -dps -append ' pf2 ';']);
                end;
            case 'No';
            case 'Cancel';
        end; % switch psfile

    else % batch mode;  assumed you want .ps files; these will go in current directory
        pf4=[pathps strtok(flmat,'.') '.ps'];
        for npost=1:numfig;
            figure(npost);
            eval(['print -dps -append ' pf4]);
        end
        close all
    end; % strcmp(btchmode,...);

    % IF IN 'SINGLE' MODE, OPTIONALLY CLOSE ALL FIGURE WINDOWS
    if ~strcmp(btchmode,'Yes');
        kclose=questdlg('Close the figure windows?');
        switch kclose;
            case 'Yes';
                close all;
            case 'No';
            case 'Cancel';
        end
    end

end; % for n=1:nfiles
