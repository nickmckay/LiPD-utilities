function L=createLiPDGoogleFile(L,overwrite)
%create lipd-web (google spreadsheet) files, L=single lipd hierarchical
%object
% % % deal with authorization on google
checkGoogleTokens;

%convert author cells to bibtex string
L = authorCell2BibtexAuthorString(L);

%if no verions, force to 1.0
if ~isfield(L,'lipdVersion')
    L.lipdVersion = 1.0;
end

if L.lipdVersion == 1.0
    display('updating LiPD file to current version')
    L = convertLiPD1_0to1_1(L);
end

if L.lipdVersion == 1.1
    display('updating LiPD file to current version')
    L = convertLiPD1_1to1_2(L);
end

%overwrite will delete the old file
if nargin<2
    overwrite=0;
end
%check to see if L already has a google file
if isfield(L,'googleSpreadSheetKey')
    if overwrite
        deleteSpreadsheet(L.googleSpreadSheetKey,aTokenDocs);
        display('deleted old google spreadsheet');
        L=rmfield(L,'googleSpreadSheetKey');
        if isfield(L,'googleMetadataWorksheet')
            L=rmfield(L,'googleMetadataWorksheet');
        end
        %also remove paleodata and chrondata worksheet keys
        
        
        for p=1:length(L.paleoData)
            for pm=1:length(L.paleoData{p}.paleoMeasurementTable)
                
                L.paleoData{p}.paleoMeasurementTable{pm}=rmfieldsoft(L.paleoData{p}.paleoMeasurementTable{pm},{'googWorkSheetKey','googleWorkSheetKey'});
                
            end
        end
        
        
        
        if isfield(L,'chronData')
            for p=1:length(L.chronData)
                for pm=1:length(L.chronData{p}.chronMeasurementTable)
                    
                    L.chronData{p}.chronMeasurementTable{pm}=rmfieldsoft(L.chronData{p}.chronMeasurementTable{pm},{'googWorkSheetKey','googleWorkSheetKey'});
                    
                end
            end
            
        end
    else
        error([L.dataSetName ' already has a google spreadsheet, you should use updateLiPDGoogleFile instead, or set to overwrite, if desired'])
    end
end

%paleoData

%this will create a new spreadsheet, with a useless first worksheet.
%We'll delete it later
spreadSheetNew=createSpreadsheet(L.dataSetName,aTokenDocs,'default.csv','text/csv');
L.googleSpreadSheetKey=spreadSheetNew.spreadsheetKey;

%now create a worksheet for each paleoDataTable
%pdNames=fieldnames(L.paleoData);
%for pd=1:length(pdNames)
dataNames={'paleo','chron'};
tableNames={'MeasurementTable','SummaryTable','EnsembleTable'};

for d=1:length(dataNames)
    if isfield(L,[dataNames{d} 'Data'])
        for pd = 1:length(L.([dataNames{d} 'Data']))
            for t=1:length(tableNames)
                if isfield(L.([dataNames{d} 'Data']){pd},[dataNames{d} tableNames{t}])
                    %go through Tables
                    for pm=1:length(L.([dataNames{d} 'Data']){pd}.([dataNames{d} tableNames{t}]))
                        L.([dataNames{d} 'Data']){pd}.([dataNames{d} tableNames{t}]){pm}=createGoogleTable( L.([dataNames{d} 'Data']){pd}.([dataNames{d} tableNames{t}]){pm},L,pd,pm,dataNames{d},tableNames{t});
                    end
                end
            end
        end
    end
end


wsNames=getWorksheetList(spreadSheetNew.spreadsheetKey,aTokenSpreadsheet);
L.googleMetadataWorksheet=wsNames(1).worksheetKey;



%metadata
%edit that first sheet to become the metadatasheet

%extract timeseries
TS=extractTimeseries(L,1);


%and also these variables
torem={'age','ageUnits','chronData','depth','depthUnits','year','yearUnits','paleoData_values',...
    'paleoData_chronDataMD5','paleoData_paleoMeasurementTableMD5','paleoData_number','paleoData_dataType','paleoData_missingValue',...
    'geo_meanLat','geo_meanElev','geo_type','geo_meanLon','pub1_identifier','pub2_identifier','pub3_identifier',...
    'pub4_identifier','pub5_identifier','pub6_identifier','pub7_identifier','pub8_identifier','pub9_identifier'};
TS=rmfieldsoft(TS,torem);


f=fieldnames(TS);
%make chunks.
baseNames=f(find(cellfun(@isempty,(strfind(f,'_')))));
geoNames=f(find(strncmpi('geo_',f,4)));


pubNames=f(find(strncmpi('pub',f,3)));
fundNames=f(find(strncmpi('fund',f,4)));
% paleoDataNames=f(find(strncmpi('paleoData_',f,10)));
% paleoDatai=(find(strncmpi('paleoData_',f,10)));
%
% cii=(find(strncmpi('climateInterpretation_',f,22)));
% cali=(find(strncmpi('calibration_',f,12)));

%instead can we grab everything with _ except chron?
underscoreI=find(~cellfun(@isempty,(strfind(f,'_'))));
chronDatai=(find(strncmpi('chronData_',f,10)));


%create top chunk, includes, base, pub and geo metadata
%how big to make it?
tcr=max([length(geoNames) length(pubNames) length(baseNames) length(fundNames)]);

if isempty(fundNames)%if no funding then
    %8columns (2 and an empty one for each
    topChunk=cell(tcr,8);
else %include 3 more for funding
    topChunk=cell(tcr,11);
end

%base first
topChunk(1:length(baseNames),1)=baseNames;
for n=1:length(baseNames)
    topChunk{n,2}=TS(1).(baseNames{n});
end

%pub second
topChunk(1:length(pubNames),4)=pubNames;
for n=1:length(pubNames)
    topChunk{n,5}=TS(1).(pubNames{n});
end

%geo third
topChunk(1:length(geoNames),7)=geoNames;
for n=1:length(geoNames)
    topChunk{n,8}=TS(1).(geoNames{n});
end
%save topChunk.mat topChunk %TROUBLESHOOTING
%funding fourth
if ~isempty(fundNames)%
    topChunk(1:length(fundNames),10)=fundNames;
    for n=1:length(fundNames)
        %         fN=TS(1).(fundNames{n}); %TROUBLESHOOTING
        %         save fn.mat fN ; %TROUBLESHOOTING
        topChunk{n,11}=TS(1).(fundNames{n});
    end
end

%make header
if ~isempty(fundNames)%
    header={'Base Metadata', ' ',' ','Publication Metadata','','','Geographic metadata','','','Funding metadata',''};
else
    header={'Base Metadata', ' ',' ','Publication Metadata','','','Geographic metadata',''};
end
%add in header
topChunk=[header ; topChunk];




%now make the paleoData chunks


%get rid of unnecessary metadata
%remove all varaibles that follow this prefix
prefixTR = {'pub','geo','funding','chron','google'};

%and also these variables
torem={'age','ageUnits','chronData','depth','depthUnits','year','yearUnits','paleoData_values',...
    'lipdVersion','archiveType','dataSetName','metadataMD5','tagMD5','paleoData_chronDataMD5','paleoData_number',...
    'paleoData_dataType','paleoData_missingValue'};
TS=rmfieldsoft(TS,torem);

for ii = 1:length(prefixTR)
    f=fieldnames(TS);
    pid = find(~cellfun(@isempty,(cellfun(@(x) x==1,strfind(f,prefixTR{ii}),'UniformOutput',0))));
    if ~isempty(pid)%remove any pub identifiers, if there are any
        TS=rmfield(TS,f(pid));
    end
end



f=fieldnames(TS);
%start with pa
paleoDatai=(find(strncmpi('paleoData_',f,10)));
cii=(find(strncmpi('climateInterpretation_',f,22)));
cali=(find(strncmpi('calibration_',f,12)));
ii=(find(strncmpi('isotopeInterpretation_',f,22)));


f = f([paleoDatai; cii ;ii ;cali]);

%make TSid first
tsi=find(strcmp('paleoData_TSid',f));
%make variableName second
vni=find(strcmp('paleoData_variableName',f));
%make description third
di=find(strcmp('paleoData_description',f));
%make units fourth
ui=find(strcmp('paleoData_units',f));

% geoi=(find(strncmpi('geo_',f,4)));
% 
% pubi=(find(strncmpi('pub',f,3)));
% fundi=(find(strncmpi('fund',f,4)));

pdCi=[tsi; vni; di; ui;  setdiff((1:length(f))',[tsi vni di ui]')];


midChunk=cell(length(TS),length(pdCi));

for p=1:length(pdCi)
    midChunk(:,p)={TS.(f{pdCi(p)})};
end

%add in the headers
h1=cell(1,size(midChunk,2));
h1{1}='paleoData column metadata';
midChunk=[h1; f(pdCi)';midChunk];
hasChron = 0;
%Chron metadatdata
if isfield(L,'chronData')
    
    CTS = flattenChronMeasurementTable(L);
    
    %remove all varaibles that follow this prefix
    prefixTR = {'pub','geo','funding','paleoData','google'};
    
    %and also these variables
    torem={'age','ageUnits','chronData','depth','depthUnits','year','yearUnits','chronData_values',...
        'lipdVersion','archiveType','dataSetName','metadataMD5','tagMD5','chronData_chronDataMD5','chronData_number'};
    CTS=rmfieldsoft(CTS,torem);
    
    for ii = 1:length(prefixTR)
        f=fieldnames(CTS);
        pid = find(~cellfun(@isempty,(cellfun(@(x) x==1,strfind(f,prefixTR{ii}),'UniformOutput',0))));
        if ~isempty(pid)%remove any pub identifiers, if there are any
            CTS=rmfield(CTS,f(pid));
        end
    end
    
    
    
    f=fieldnames(CTS);
    
    chronDatai=(find(strncmpi('chronData_',f,10)));


f = f(chronDatai);
    
    
    %now make chron data chunk
    tsi=find(strcmp('chronData_TSid',f));
    %make variableName second
    vni=find(strcmp('chronData_variableName',f));
    %make description third
    di=find(strcmp('chronData_description',f));
    %make units fourth
    ui=find(strcmp('chronData_units',f));
    %make measurementMaterial fourth
    mi=find(strcmp('chronData_measurementMaterial',f));
    
    
    
    
    
    pdCi=[tsi; vni; di; ui; mi;  setdiff((1:length(f))',[tsi vni di ui mi])];
    botChunk=cell(length(CTS),length(pdCi));
    
    for p=1:length(pdCi)
        botChunk(:,p)={CTS.(f{pdCi(p)})};
    end
    
    %add in the headers
    h1=cell(1,size(botChunk,2));
    h1{1}='chronData column metadata';
    botChunk=[h1; f(pdCi)';botChunk];
else
    %create an empty bottom chunk
    
    botChunk=cell(1,size(midChunk,2));
    
end


%NOW COMBINE!!!!!!!!!
%combine the two chunks
nrow=size(topChunk,1)+size(botChunk,1)+size(midChunk,1)+2;

ncol=max([size(topChunk,2),size(midChunk,2),size(botChunk,2)]);

%make final cell to be written to google
metadataCell=cell(nrow,ncol);
metadataCell(1:size(topChunk,1),1:size(topChunk,2))=topChunk;
metadataCell((size(topChunk,1)+2):(size(topChunk,1)+2+size(midChunk,1)-1),1:size(midChunk,2))=midChunk;
metadataCell((nrow-size(botChunk,1)+1):end,1:size(botChunk,2))=botChunk;

%make all the cell entries strings
%save dum.mat metadataCell %troubleshooting
metadataCell4Goog=stringifyCells(metadataCell);

%Remove FORBIDDEN characters from metadataCell4Goog
%these include:  ' 
toRemove = {''''};
metadataCell4Goog=strRemoveCell(metadataCell4Goog,toRemove);


%now write this into the first worksheet
changeWorksheetNameAndSize(spreadSheetNew.spreadsheetKey,wsNames(1).worksheetKey,nrow,ncol,'metadata',aTokenSpreadsheet);





for m=1:ncol
    editWorksheetColumn(spreadSheetNew.spreadsheetKey,wsNames(1).worksheetKey,m,1:nrow,metadataCell4Goog(:,m),aTokenSpreadsheet);
end

L = BibtexAuthorString2Cell(L);


