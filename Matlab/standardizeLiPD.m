function newL = standardizeLiPD(L)

%standardize key and value names in a LiPD file

%first, check for year or age field. 

for p =1:length(L.paleoData)
    
    for n=1:length(L.paleoData{p}.paleoMeasurementTable)
        PMT = L.paleoData{p}.paleoMeasurementTable{n};
        colnames = structFieldNames(PMT);
        if ~any(strcmp('age',colnames) | strcmp('year',colnames))
            display(strcat(num2str((1:length(colnames))'),repmat({' - '},length(colnames),1),colnames))
            wc = input('Which column is the primary age/year column for this paleoData table? ');
            ay = input('Is this an "age" column (enter 1) or a year column (enter 0)');
            if ay
                PMT.age=PMT.(colnames{wc});
                PMT.age.variableName = 'age';
                PMT=rmfield(PMT,colnames{wc});
            else
                PMT.year=PMT.(colnames{wc});
                PMT.year.variableName = 'year';
                PMT=rmfield(PMT,colnames{wc});
            end
            
        end
        L.paleoData{p}.paleoMeasurementTable{n}=PMT;
    end
end
TS = extractTimeseries(L);

TS = renameTS(TS);

load nameCon.mat
toCon = fieldnames(nameCon);

for i = 1:length(toCon)
   TS = convertNamesTS(TS,toCon{i});
end

newL = collapseTS(TS);
