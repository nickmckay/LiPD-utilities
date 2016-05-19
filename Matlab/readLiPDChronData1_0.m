function C=readLiPDChronData1_0(I,dirname)


toct=NaN;
if isfield(I,'chronData')
    toct=1:length(I.chronData);
end


%C=I.chronData;

if ~isnan(toct) %if there are chron tables, load em in
    for i = toct; %go through each chronology
        %%%%%CHRON MEASUREMENT TABLE
        %Go through chronMeasurementTable first
        cT = I.chronData{i};
        
        cT=readLiPDTable(cT,dirname);
        cT=processLiPDColumns(cT);
        cT.chronMD5 = I.chronMD5;
        if i==1
            C.(matlab.lang.makeValidName(cT.chronDataTableName))=cT;
        else
            C.(matlab.lang.makeUniqueStrings(cT.chronDataTableName,fieldnames(C)))=cT;
        end
               
        %%%%%%END CHRON MEASUREMENT TABLE
    end
else
C=NaN;
end