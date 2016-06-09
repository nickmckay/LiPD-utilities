function newL = standardizeLiPD(L)

%standardize key and value names in a LiPD file

%first, check for year or age field. 
pdnames = structFieldNames(L.paleoData);
npd = length(pdnames);
for n=1:npd
    colnames = structFieldNames(L.paleoData.(pdnames{n}));
    if ~any(strcmp('age',colnames) | strcmp('year',colnames))
       display(strcat(num2str((1:length(colnames))'),repmat({' - '},length(colnames),1),colnames))
       wc = input('Which column is the primary age/year column for this paleoData table? ');
       ay = input('Is this an "age" column (enter 1) or a year column (enter 0)');
       if ay
           L.paleoData.(pdnames{n}).age=L.paleoData.(pdnames{n}).(colnames{wc});
           L.paleoData.(pdnames{n}).age.variableName = 'age';
           L.paleoData.(pdnames{n})=rmfield(L.paleoData.(pdnames{n}),colnames{wc});
       else
            L.paleoData.(pdnames{n}).year=L.paleoData.(pdnames{n}).(colnames{wc});
           L.paleoData.(pdnames{n}).year.variableName = 'year';
           L.paleoData.(pdnames{n})=rmfield(L.paleoData.(pdnames{n}),colnames{wc});
       end
           
    end
end
TS = extractTimeseriesLiPD(L);

TS = renameTS(TS);

load nameCon.mat
toCon = fieldnames(nameCon);

for i = 1:length(toCon)
   TS = convertNamesTS(TS,toCon{i});
end

newL = collapseTS(TS);
