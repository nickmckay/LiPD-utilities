function cmt = baconInput2ChronMeasurementTable(filename,units)
%import bacon input into chronData


%units cell that describes calibrated age units, depth units, and 14C age
%units.

%default:
if nargin <2
    units = {'cal yr','cm','14C yr'};
end

if nargin==0
    [filename,pathname] = uigetfile('*.csv','Pick a BACON input file');
    filename=[pathname filename];
elseif isnan(filename)
    [filename,pathname] = uigetfile('*.csv','Pick a BACON input file');
    filename=[pathname filename];
end

%read the csv file
bacIn = readtable(filename);
fnames = fieldnames(bacIn);


%convert cells to double if necessary
for f=2:length(fnames)
    if iscell(bacIn.(fnames{f}))
        bacIn.(fnames{f}) = cell2num(bacIn.(fnames{f}));
    end
end



%separate 14c from calibrated ages
c14In = find(bacIn.cc>0);
if length(c14In) > 0
    %copy c14ages to new column
    bacIn.age14C = nan(length(bacIn.age),1);
    bacIn.age14C(c14In)=bacIn.age(c14In);
    bacIn.age(c14In) = nan(length(c14In),1);
    %and uncertainty
    bacIn.age14CUncertainty = nan(length(bacIn.age),1);
    bacIn.age14CUncertainty(c14In)=bacIn.error(c14In);
    bacIn.error(c14In) = nan(length(c14In),1);
end

colToImport = {'id','age','error','depth','dR','dSTD','age14C','age14CUncertainty'};
varNames = {'labID','age','ageUncertainty','depth','deltaR','deltaRUncertainty','age14C','age14CUncertainty'};
unitsCell = {'unitless',units{1},units{1},units{2},units{3},units{3},units{3},units{3}};

for i =1:length(colToImport)
    if any(strcmp(fieldnames(bacIn),colToImport{i}))
        skip=0;
        if ~iscell(bacIn.(colToImport{i}))
            if all(bacIn.(colToImport{i})==0)%don't import if they're all zero
                skip=1;
            end
        end
        
        if ~skip
            cmt{1}.(varNames{i}).values = bacIn.(colToImport{i});
            cmt{1}.(varNames{i}).units = unitsCell{i};
            cmt{1}.(varNames{i}).variableName = varNames{i};
        end
    end
end

