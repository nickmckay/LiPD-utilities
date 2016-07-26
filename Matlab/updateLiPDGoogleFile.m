function L=updateLiPDGoogleFile(L,createIfNeeded)
%updates the google version of LiPD file that already exists
% % % deal with authorization on google
checkGoogleTokens;
L = authorCell2BibtexAuthorString(L);

if nargin<2
    createIfNeeded=0;
end
%check to see if L already has a google file
if ~isfield(L,'googleSpreadSheetKey')
    if ~createIfNeeded
        error([L.dataSetName ' does not already have a google spreadsheet, you should use createLiPDGoogleFile instead'])
    else
        L=createLiPDGoogleFile(L);
    end
else
    rewrite=0; %by default, we're doing nothing to this spreadsheet
    %check to see if the tagMD5's are the same
    wl=getWorksheetList(L.googleSpreadSheetKey,aTokenSpreadsheet);
    
    
    if ~isfield(L,'googleMetadataWorksheet')
        L.googleMetadataWorksheet=wl(1).worksheetKey;
    end
    col1=getWorksheetColumn(L.googleSpreadSheetKey,L.googleMetadataWorksheet,1,aTokenSpreadsheet,0);
    tr=find(strcmp('tagMD5',col1));
    
    if isempty(tr)
        rewrite=2;%if there is no tag MD5
    else
        googTagMD5=getWorksheetCell(L.googleSpreadSheetKey,L.googleMetadataWorksheet,tr,2,aTokenSpreadsheet);
        if ~strcmp(L.tagMD5,googTagMD5)
            rewrite=1;%or if it's not the same, rewrite
        end
    end
    
    if rewrite>0
        if rewrite==1
            display([L.dataSetName ': MD5 tags dont match - updating spreadsheet'])
        else
            display([L.dataSetName ': NO MD5 tag on google - updating spreadsheet'])
        end
        

        
        %just make new ones
        %first delete all but metadata
        for w=2:length(wl)
            deleteWorksheet(L.googleSpreadSheetKey,wl(w).worksheetKey,aTokenSpreadsheet);
        end
        
        
        
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
        
        %what worksheets do we have
        
        wsNames=getWorksheetList(L.googleSpreadSheetKey,aTokenSpreadsheet);
        L.googleMetadataWorksheet=wsNames(1).worksheetKey;
        
        
        
        %Now metadata the same for all cases
        %metadata
        %edit that first sheet to become the metadatasheet
        
        %metadata
        %edit that first sheet to become the metadatasheet
        
        %extract timeseries
        TS=extractTimeseries(L,1);
        
        
        %and also these variables
        torem={'age','ageUnits','chronData','depth','depthUnits','year','yearUnits','paleoData_values',...
            'paleoData_chronDataMD5','paleoData_number','paleoData_dataType','paleoData_missingValue',...
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
            'LiPDVersion','archiveType','dataSetName','metadataMD5','tagMD5','paleoData_chronDataMD5','paleoData_number',...
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
                'LiPDVersion','archiveType','dataSetName','metadataMD5','tagMD5','chronData_chronDataMD5','chronData_number'};
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
        save debug.mat metadataCell
        metadataCell4Goog=stringifyCells(metadataCell);
        
        %now write this into the first worksheet
        changeWorksheetNameAndSize(L.googleSpreadSheetKey,wsNames(1).worksheetKey,nrow,ncol,'metadata',aTokenSpreadsheet);
        
        for m=1:ncol
            editWorksheetColumn(L.googleSpreadSheetKey,wsNames(1).worksheetKey,m,1:nrow,metadataCell4Goog(:,m),aTokenSpreadsheet);
        end
        
        L = BibtexAuthorString2Cell(L);
    end
end
