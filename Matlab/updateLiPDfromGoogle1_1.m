function L=updateLiPDfromGoogle1_1(L)

checkGoogleTokens
%what are the metadata worksheetKeys
wl = getWorksheetList(L.googleSpreadSheetKey,aTokenSpreadsheet);
spreadsheetkey = L.googleSpreadSheetKey;
wknames = {wl.worksheetTitle}';
wkKeys = {wl.worksheetKey}';

mki = find(strcmpi('metadata',wknames));
pdi = find(strncmpi('paleodata',wknames,9));
cdi = find(strncmpi('chrondata',wknames,9));

if length(mki)~=1
    error('There must be one, and only one, metadata worksheet, and it must be named "Metadata"')
end

if length(pdi)==0
    error('There must be at least one paleodata worksheet, and it must start with "Paleodata"')
end

for i = 1:length(pdi)
    fullName = wknames{pdi(i)};
    dashin =min(strfind(fullName,'-'));
    if isempty(dashin)
        error('the paleodata worksheets must be named "paleoData-tableName", where tableName is whatever name you want')
    end
    pdwknames{i} =  fullName((dashin+1):end);
    pdwkkeys{i} =  wkKeys{pdi(i)};
    
end

if length(cdi)>0
    for i = 1:length(cdi)
        fullName = wknames{cdi(i)};
        dashin =min(strfind(fullName,'-'));
        if isempty(dashin)
            error('the chrondata worksheets must be named "chronData-tableName", where tableName is whatever name you want')
        end
        cdwknames{i} =  fullName((dashin+1):end);
        cdwkkeys{i} =  wkKeys{cdi(i)};
        
    end
end


metadataKey = wkKeys{mki};



%make a google version of the TS file
%metadata first
[GTS,GTSC]=getLiPDGoogleMetadata(spreadsheetkey,metadataKey);

%check to see if the paleodata worksheet keys are stored
if ~isfield(GTS,'paleoData_googleWorkSheetKey')
    if ~isfield(GTS,'paleoData_paleoDataTableName')
        if length(pdwkkeys)==1
            repcells = repmat({pdwkkeys{1}},length(GTS),1);
            [GTS.paleoData_googleWorkSheetKey] = repcells{:};
        else
            bc = cell(length(GTS),1);
            [GTS.paleoData_googleWorkSheetKey] = bc{:};
        end
    else
         bc = cell(length(GTS),1);
            [GTS.paleoData_googleWorkSheetKey] = bc{:};
    end
end
pdgwk={GTS.paleoData_googleWorkSheetKey}';
if any(cellfun(@isempty,pdgwk)) %see if any are missing keys
    %make sure there are names
    if ~isfield(GTS,'paleoData_paleoDataTableName')
        
        error('the TS metadata must include at least paleoDataTableName or googleWorksheetKey')
    end
    pdtNames = {GTS.paleoData_paleoDataTableName}';
    ie = find(cellfun(@isempty,pdgwk)); %identify which are missing keys
    for pie = 1:length(ie)
        %match the name to the
        whichPDTsheet = find(strcmp(pdtNames{ie(pie)},pdwknames));
        if isempty(whichPDTsheet)
            if length(pdwknames)==1
                warning(['Cant find a paleodata worksheet named ' pdtNames{ie(pie)} '; but guessing that it is ' pdwknames{1}])
                whichPDTsheet=1;
            else
                error(['Cant find a paleodata worksheet named ' pdtNames{ie(pie)}])
            end
        end
      
        
        pdgwk{ie(pie)}=pdwkkeys{whichPDTsheet};
        display(['Infilling worksheet key ' pdgwk{ie(pie)} ' for paleoData sheet ' pdtNames{ie(pie)} ])
    end
    [GTS.paleoData_googleWorkSheetKey] = pdgwk{:};
end


%then grab the paleodata
GTS=getLiPDGooglePaleoData(GTS);

%make sure not character columns
%ischar(GTS(2).paleoData_values)


%add in special fields (year, depth, age)
yy=find(strcmpi('year',{GTS.paleoData_variableName}'));
if ~isempty(yy)
    dum=repmat({GTS(yy).paleoData_values},length(GTS),1);
    [GTS.year]=dum{:};
    dum=repmat({GTS(yy).paleoData_units},length(GTS),1);
    [GTS.yearUnits]=dum{:};
end
aa=find(strcmpi('age',{GTS.paleoData_variableName}'));
if ~isempty(aa)
    dum=repmat({GTS(aa).paleoData_values},length(GTS),1);
    [GTS.age]=dum{:};
    dum=repmat({GTS(aa).paleoData_units},length(GTS),1);
    [GTS.ageUnits]=dum{:};
end
dd=find(strcmpi('depth',{GTS.paleoData_variableName}'));
if ~isempty(dd)
    dum=repmat({GTS(dd).paleoData_values},length(GTS),1);
    [GTS.depth]=dum{:};
    dum=repmat({GTS(dd).paleoData_units},length(GTS),1);
    [GTS.depthUnits]=dum{:};
end

%if there's a chronology, grab that too
if isstruct(GTSC)
    
    %check to see if the chrondata worksheet keys are stored
    if ~isfield(GTSC,'chronData_googleWorkSheetKey')
        if ~isfield(GTSC,'chronData_chronDataTableName')
            
            if length(cdwkkeys)==1
                repcells = repmat({cdwkkeys{1}},length(GTSC),1);
                [GTSC.chronData_googleWorkSheetKey] = repcells{:};
            else
                
                bc = cell(length(GTSC),1);
                [GTSC.chronData_googleWorkSheetKey] = bc{:};
            end
        else
            bc = cell(length(GTSC),1);
            [GTSC.chronData_googleWorkSheetKey] = bc{:};
        end
        
    end
    
    
    
     
    cdgwk={GTSC.chronData_googleWorkSheetKey}';
    if any(cellfun(@isempty,cdgwk)) %see if any are missing keys
        %make sure there are names
        if ~isfield(GTSC,'chronData_chronName')
            if isfield(GTSC,'chronData_chronDataTableName')
                [GTSC.chronData_chronName]=GTSC.chronData_chronDataTableName;
            else
                
                error([GTS.dataSetName ': the chron metadata must include at least chronName or googleWorksheetKey'])
            end
        end
        cdtNames = {GTSC.chronData_chronName}';
        ie = find(cellfun(@isempty,cdgwk)); %identify which are missing keys
        for pie = 1:length(ie)
            %match the name to the
            whichCDTsheet = find(strcmp(cdtNames{ie(pie)},cdwknames));
            
            if isempty(whichCDTsheet)
                if length(cdwknames)==1
                    warning(['Cant find a chronology worksheet named ' cdtNames{ie(pie)} '; but guessing that it is ' cdwknames{1}])
                    whichCDTsheet=1;
                else
                    error(['Cant find a chronology worksheet named ' cdtNames{ie(pie)}])
                end
            end
            cdgwk{ie(pie)}=cdwkkeys{whichCDTsheet};
            display(['Infilling worksheet key ' cdgwk{ie(pie)} ' for chronData sheet ' cdtNames{ie(pie)} ])
        end
        [GTSC.chronData_googleWorkSheetKey] = cdgwk{:};
    end
    
    
    GTSC=getLiPDGoogleChronData(GTSC);
    
    %collapse the chron TS
    CD=collapseTSChron(GTSC);
    CD=rmfieldsoft(CD,'LiPDVersion');
    %CD should only inlcude one file... if it doesn't then thats a problem.
    cnames=fieldnames(CD);
    
    
    if length(cnames)>1
        error('there shouldnt be multiple dataset Names within one dataset')
    end
    
    %assign the chron structure.
    chronData=CD.chronData;
    
end
%new structure
%start with the old one
LTS = extractTimeseries(L);
NTS=LTS;

%are there any fields that are new?
newFields=setdiff(fieldnames(GTS),fieldnames(LTS));

if length(newFields)>0
    bc=repmat({''},length(NTS),1);
    %then you have to deal with new fields...
    for n=1:length(newFields)
        [NTS.(newFields{n})]=bc{:};
    end
end

%are there more TSs?
if length(NTS)<length(GTS) %yep
    Ln=length(NTS);
    %then replicate some of them
    while length(NTS)<length(GTS)
        NTS(Ln+1)=NTS(Ln);
        Ln=Ln+1;
    end
end

%are there less TSs?
if length(NTS)>length(GTS) %yep
    %then truncate some of them
    NTS=NTS(1:length(GTS));
end

%now go through all the fields and replace with google if they changed
anyChanges=0;
gnames=fieldnames(GTS);
for g=1:length(gnames)
    O={NTS.(gnames{g})}';
    N={GTS.(gnames{g})}';
    if ~isequal(O,N)%check to see if it changed,
        anyChanges=1;
        display(['updating ' (gnames{g})])
        [NTS.(gnames{g})]=N{:};
    end
end

if isstruct(GTSC)
    for tl=1:length(GTS)
        NTS(tl).chronData=chronData;
    end
end


L=collapseTS(NTS,1);

L = BibtexAuthorString2Cell(L);
