clear MT
%pull from ID
measName = 'TRW';
measUnits = 'mm';
%Table to measurementTable

%measurements first (raw ring widths)
M=X.measurements;
%year
MT.year.values = M.Time;
MT.year.units = 'AD';
MT.year.variableName = 'year';





%now measurements
for i = 1:length(M.ID)
    thisName = [measName '_' M.ID{i}];
    
MT.(thisName).variableName = thisName;
MT.(thisName).proxyObservationType = measName;
MT.(thisName).units = measUnits;
MT.(thisName).values = M.Data(:,i);
        
end

%add in chronology (If chronology is not always the same length as the
%data, we should handle this differently.

%chronology.
%make sure same time axis
if all(X.chronology.Time==X.measurements.Time)
    chronName = [measName '_chronology'];
MT.(chronName).values = X.chronology.Data;
MT.(chronName).variableName = chronName;
MT.(chronName).units = 'unitless';
MT.(chronName).proxyObservationType = measName;
else
    error('Chronology and measurement years dont match')
end

%table metadata
MT.chronologyURL = X.chronology.url;
MT.measurementURL = X.measurements.url;








