function L=convertLiPD1_2to1_3(L,forceConvert)


if nargin<2
    forceConvert = 0;
end

if ~isfield(L,'lipdVersion')
    
    L.lipdVersion = 1.0;
end

if ischar(L.lipdVersion)
    L.lipdVersion = str2num(L.lipdVersion);
end

if L.lipdVersion == 1.2 | forceConvert
    %handle chronData first
    if isfield(L,'chronData')
        
        for i = 1:length(L.chronData);
            C=L.chronData{i};
            if isfield(C,'chronMeasurementTable')
                C.measurementTable = C.chronMeasurementTable;
                C = rmfield(C,'chronMeasurementTable');
                for mt=1:length(C.measurementTable)
                    if isfield(C.measurementTable{mt},'chronMeasurementTableName')
                        C.measurementTable{mt}.measurementTableName = C.measurementTable{mt}.chronMeasurementTableName;
                        C.measurementTable{mt} = rmfield(C.measurementTable{mt},'chronMeasurementTableName');
                    end
                end
            end
            
            if isfield(C,'chronModel')
                C.model =  C.chronModel;
                C = rmfield(C,'chronModel');
                for j=1:length(C.model)
                    CM=C.model{j};
                    if isfield(CM,'summaryTable')
                        newSum = cell(1,1);
                        newSum{1} = CM.summaryTable;
                        CM.summaryTable=newSum;
                    end
                    if isfield(CM,'ensembleTable')
                        newEns = cell(1,1);
                        newEns{1} = CM.ensembleTable;
                        CM.ensembleTable=newEns;
                    end
                    C.model{j} = CM;
                end
            end
            L.chronData{i}=C;
        end
    end
    
    %now PaleoData changes.
    if isfield(L,'paleoData')
        
        for i = 1:length(L.paleoData);
            C=L.paleoData{i};
            if isfield(C,'paleoMeasurementTable')
                C.measurementTable = C.paleoMeasurementTable;
                C = rmfield(C,'paleoMeasurementTable');
                for mt = 1:length(C.measurementTable)
                    if isfield(C.measurementTable{mt},'paleoMeasurementTableName')
                        C.measurementTable{mt}.measurementTableName = C.measurementTable{mt}.paleoMeasurementTableName;
                        C.measurementTable{mt} = rmfield(C.measurementTable{mt},'paleoMeasurementTableName');
                    end
                    %deal with interpretation
                    MT = C.measurementTable{mt};
                    mtn = structFieldNames(MT);
                    for m =1:length(mtn)
                        col = MT.(mtn{m});
                        if isfield(col,'climateInterpretation')
                            col.interpretation  = cell(1,1);
                            col.interpretation{1} = col.climateInterpretation;
                            col = rmfield(col,'climateInterpretation');
                        end

                        %for isotope interpretation, make each independent
                        %variable an interpretation entry...
                        if isfield(col,'isotopeInterpretation')
                            if ~isfield(col.isotopeInterpretation,'independentVariable')
                                warning('theres no independentVariable, creating an empty one')
                                col.isotopeInterpretation.independentVariable{1}.name = 'missing';
                            end
                            %grab the root level isotope interpretation
                            intnames = setdiff(fieldnames(col.isotopeInterpretation),'independentVariable');

                            for iv = 1:length(col.isotopeInterpretation.independentVariable)
                                newInterp = col.isotopeInterpretation.independentVariable{iv};
                                if isfield(newInterp,'name')
                                    newInterp.variable = newInterp.name;
                                else
                                    newInterp.variable = 'missing';
                                end

                                newInterp = rmfieldsoft(newInterp,'name');
                                for intn = 1:length(intnames)
                                   newInterp.(intnames{intn}) = col.isotopeInterpretation.(intnames{intn});
                                end
                                newInterp.scope = 'isotope';
                                
                                 if isfield(col,'interpretation')
                                    col.interpretation{length(col.interpretation)+1} = newInterp;
                                 else
                                     col.interpretation = cell(1,1);
                                     col.interpretation{1} = newInterp;
                                 end
                            end
                            
                           
                            col = rmfield(col,'isotopeInterpretation');
                        end
                        MT.(mtn{m}) = col;
                        
                    end
                    C.measurementTable{mt} = MT;
                    
                end
            end
            
            if isfield(C,'paleoModel')
                C.model =  C.paleoModel;
                C = rmfield(C,'paleoModel');
                for j=1:length(C.model)
                    
                    CM=C.model{j};
                    
                    if isfield(CM,'summaryTable')
                        newSum = cell(1,1);
                        newSum{1} = CM.summaryTable;
                        CM.summaryTable=newSum;
                    end
                    if isfield(CM,'ensembleTable')
                        newEns = cell(1,1);
                        newEns{1} = CM.ensembleTable;
                        CM.ensembleTable=newEns;
                    end
                    C.model{j} = CM;
                end
            end
            L.paleoData{i}=C;
        end
    end
    
    
    
    L.lipdVersion = 1.3;
    
end

