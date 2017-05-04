

% function pages2k_phase2_db_synopsis(vers,options)
%  INPUT:   vers (version of the database, string)
%           (optional) export. If true, exports figures to pdf. If not,
%           simply prints them to screen. [default =0]
%
% WHAT: plot space time map of TS data 
%
% WHO/WHEN started Dec 5 2014 by Julien Emile-Geay (USC)
%Adapted for LiPD Utilities by Nick McKay (NAU)
inset = 0;
% process options
if nargin < 2
    options.export = 0;
end
year = [];
% load data and packages
%addpath(genpath('../utilities'));
%load(['../../data/proxy_db/pages2kTSv' vers '_unpack.mat'])
FontName = 'Helvetica';
set(0,'defaultAxesFontName', FontName)
set(0,'defaultTextFontName', FontName)
style_t = {'FontName',FontName,'Fontweight','Bold','Fontsize',16};
style_l = {'FontName',FontName};
%figpath = '../../figs/synopsis/';

%%
%pull relevant data from TS
archive={TS.archiveType}';
year=1:2000;
nr=length(TS);
yearMin={TS.minYear}';
emptyYearMin = find(cellfun(@isempty,yearMin));
yearMin(emptyYearMin)=repmat({NaN},length(emptyYearMin),1);
yearMin=cell2mat(yearMin);

yearMax={TS.maxYear}';
emptyYearMax = find(cellfun(@isempty,yearMax));
yearMax(emptyYearMax)=repmat({NaN},length(emptyYearMax),1);
yearMax=cell2mat(yearMax);

vers='0.3';

p_lon=cell2mat({TS.geo_meanLon}');
p_lat=cell2mat({TS.geo_meanLat}');

%%
% extract archive types and assign colors
% =========================================
% fix inconsistencies
%archive = strrep(archive,'Tree Ring','tree');
%archive = strrep(archive,'documents','historic');
%archive = strrep(archive,'historical','historic');
%archive = strrep(archive,'lake','Lake sediment');
%archive(strcmp('ice',archive))={'ice core'};
%archive(cellfun(@isempty,archive))={'n/a'};
% Graphical Attributes of each proxy type
archiveType = unique(lower(archive)); na = length(archiveType);

Graph{1,1}=rgb('DarkOrange');  Graph{1,2}= 'o'; 
Graph{2,1}=rgb('LightSkyBlue');Graph{2,2}= 'd';
Graph{3,1}=rgb('SaddleBrown'); Graph{3,2}= 's'; 
Graph{4,1}=rgb('Red');         Graph{4,2}= 'o'; 
Graph{5,1}=rgb('RoyalBlue');   Graph{5,2}= 's'; 
Graph{6,1}=rgb('Black');       Graph{6,2}= 'p'; 
Graph{7,1}=rgb('DarkKhaki');   Graph{7,2}= 'h'; 
Graph{8,1}=rgb('DeepSkyBlue'); Graph{8,2}= 's'; 
Graph{9,1}=rgb('Gold');        Graph{9,2}= 'h';
Graph{10,1}=rgb('DeepPink');   Graph{10,2}= 'd';
Graph{11,1}=rgb('LimeGreen');  Graph{11,2}= '^'; 

if na>size(Graph,1)
    error('More than 11 archive types. Beyond current functionality')
end
Graph=Graph(1:na,:);


%%
% DEFINE TIME AXIS AND AVAILABILITY
% avail = ~isnan(proxy);
ny = length(year);
avail = NaN(ny,nr);

p_code = nan(nr,1);
for r = 1:nr
    % define proxy code
    s = strfind(archiveType,lower(archive{r}));
    p_code(r) =  find(~cellfun('isempty', s), 1 ); % number between 1 and na
    avail(ismember(year,[yearMin(r):yearMax(r)]),r)=1;
end

% define edge color (black except for hybrids)
edgec = cell(nr,1);
edgec(1:nr) = {'none'};%{rgb('Black')};
if na>=6
edgec(p_code == 6) = {Graph{6,1}};
end

nproxy = zeros(ny,na); pind = zeros(na,1);
for a = 1:na % loop over archive types
    nproxy(:,a) = sum(~isnan(avail(:,p_code == a)),2);
    pind(a) = find(p_code == a,1,'first');
    nArch(a)   = sum(p_code == a);
    leg_lbl{a} = [archiveType{a} ' (' int2str(nArch(a)) ')'];
    %disp(leg_lbl{a})
end

% =============
% PLOT SPACETIME COVERAGE
% =============
n1000 = ceil(sum(nproxy(year == 1000,:))/10)*10;
ns    = length(unique({TS.dataSetName})); % # of sites
versl = strrep(vers,'_','.');
fig('PAGES2K'), clf
orient landscape
set(gcf,'PaperPositionMode','auto')
set(gcf, 'Position', [440   144   896   654])
% plot spatial distribution
hmap=axes('Position', [.05 0.45 0.75 0.5]);
m_proj('Robinson','clong',10);
m_coast('patch',[.9 .9 .9]);
m_grid('xtick',6,'ytick',9,'xticklabel',[ ],'xlabeldir','middle', 'fontsize',4,'fontname',FontName);
% loop over records
for r = 1:nr
    h(r) = m_line(p_lon(r),p_lat(r),'marker',Graph{p_code(r),2},'MarkerEdgeColor',edgec{r},'MarkerFaceColor',Graph{p_code(r),1},'linewidth',[1],'MarkerSize',[7],'linestyle','none');
end
text(-2,1.75,['Iso2k network version ' versl ' (',int2str(nr) , ' records from ', int2str(ns), ' sites)'],style_t{:});
% legend
hl = legend(h(pind),leg_lbl,'location',[.84 .6 .1 .2],style_l{:});
set(hl, 'FontName', FontName,'box','off');
% TEMPORAL AVAILABILITY
hstack=axes('Position', [0.1 0.1 0.8 0.29]);
cmap=cell2mat(Graph(:,1));
colormap(cmap);
area(year,nproxy,'EdgeColor','w'), set(gca,'YAxisLocation','Right');
xlim([1 2000])
fancyplot_deco('','Year (CE)','# proxies',14,'Helvetica');
title('Temporal Availability',style_t{:})
% inset
if inset
frac=.5;
hstackin=axes('Position', [0.1 0.2 frac*.8 0.14]);
area(year,nproxy,'EdgeColor','w')
axis([1 1000 0 n1000])
set(hstackin,'xtick',[],'box','off','TickDir','out','TickLength',[.02 .02],'YMinorTick','on', 'YGrid','on')
set(hstackin,'YAxisLocation','Right')
set(hstackin,'FontName',FontName,'YColor', [.3 .3 .3])
title('First Millennium',style_l{:})
end
%pause; % manually adjust the size of the figure
if options.export
   %figpath = [strrep(userpath,':','/') 'tempfigs/'];
   fname = ['Iso2k_' vers '_spacetime_realData.png'];
   export_fig([fname],'-r300');
   %hepta_figprint(['../../figs/synopsis/PAGES2K_phase2_' vers '_spacetime']);
   %saveFigure([figpath fname '_saveFigure.pdf']); %'painters', true
   %plot2svg([figpath fname '.svg']);
   %print([figpath fname],'-depsc','-r300','-cmyk')
end
