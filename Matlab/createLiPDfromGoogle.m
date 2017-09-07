function [L,GTS]=createLiPDfromGoogle(spreadsheetkey)

%get sheets metadata
checkGoogleTokens;

%what are the metadata worksheetKeys
wl = getWorksheetList(spreadsheetkey,aTokenSpreadsheet);
wknames = {wl.worksheetTitle}';
wkKeys = {wl.worksheetKey}';

mki = find(strcmpi('metadata',wknames));
pdi = find(strncmpi('paleo',wknames,5));
cdi = find(strncmpi('chron',wknames,5));

if length(mki)~=1
    error('There must be one, and only one, metadata worksheet, and it must be named "Metadata"')
end

if length(pdi)==0
    error('There must be at least one paleodata worksheet, and it must start with "paleo"')
end

metadataKey = wkKeys{mki};


%make a google version of the TS file
%metadata first
[GTS,GTSC]=getLiPDGoogleMetadata(spreadsheetkey,metadataKey);

for i = 1:length(pdi)
    fullName = wknames{pdi(i)};
    
    dashin =min(strfind(fullName,'-'));
    numbers=regexp(fullName,'[0-9]');
    if length(numbers)<2 | length(numbers)>3
                error('the paleodata worksheets must be named "paleo{x}-tableName{y}", where {x} and {y} are integers')
    end
    if isempty(dashin)
        error('the paleodata worksheets must be named "paleo{x}-tableName{y}", where tableName is the type of table')
    end
    paleoTableNames{i} =  fullName((dashin+1):(end-1));
    ptn(i,:)=numbers(1:2);
    pdwkkeys{i} =  wkKeys{pdi(i)};
    
end

%check to see if the paleodata worksheet keys are stored
if ~isfield(GTS,'paleoData_googleWorkSheetKey')
    bc = cell(length(GTS),1);
    [GTS.paleoData_googleWorkSheetKey] = bc{:};
end
pdgwk={GTS.paleoData_googleWorkSheetKey}';
if any(cellfun(@isempty,pdgwk)) %see if any are missing keys
 %   make sure there are names
    if ~isfield(GTS,'paleoData_paleoNumber')
        error('the TS metadata must include the paleoNumber (which paleo object - first number in table name)');
    end
    
%    figure out table types
    gtsnames = fieldnames(GTS);
    tni=find(~cellfun(@isempty,(strfind(gtsnames,'TableNumber'))));
    tableType=cell(1,1);
    clear tableNumber

    for tn=1:length(tni)
            gg=find(~cellfun(@isempty,{GTS.(gtsnames{tni})}));
            usi=strfind(gtsnames{tni},'_');
            tableType(gg,tn)={gtsnames{tni}((usi+6):(end-11))};
            tableNumber(:,tn)={GTS.(gtsnames{tni})}';
    end
    
    if size(tableNumber,1)~=length(gg)
       error('There are inconsistencies in the number of columns in your paleodata table metadata. Could just be an extra empty row at the bottom (there should only be one)'); 
    end
    
    if size(tableType,2)>1
        if any(sum(~cellfun(@isempty,tableType),2)~=1)
          error('There must be exactly 1 "tableNumber" entry in each row')  
        end
        tableType=tableType(~cellfun(@isempty,tableType));
    end
    
    one=repmat({'paleo'},length(GTS),1);
    two={GTS.paleoData_paleoNumber}';
    three=tableType;
    four=tableNumber;
    tableName=strcat(one, two, repmat({'-'},length(GTS),1) ,three,repmat({'Table'},length(GTS),1), four);
    
    for pie = 1:length(GTS)
%        match the name to the
        whichPDTsheet = find(strcmp(tableName{pie},wknames));
        pdgwk{pie}=wkKeys{whichPDTsheet};
        display(['Infilling worksheet key ' pdgwk{pie} ' for paleoData sheet ' tableName{pie} ])
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
    for i = 1:length(cdi)
        fullName = wknames{cdi(i)};
        
        dashin =min(strfind(fullName,'-'));
        numbers=regexp(fullName,'[0-9]');
        if length(numbers)~=2
            error('the chrondata worksheets must be named "chron{x}-tableName{y}", where {x} and {y} are integers')
        end
        if isempty(dashin)
            error('the chrondata worksheets must be named "chron{x}-tableName{y}", where tableName is the type of table')
        end
        chronTableNames{i} =  fullName((dashin+1):(end-1));
        ctn(i,:)=numbers;
        cdwkkeys{i} =  wkKeys{cdi(i)};
        
    end
    
    %check to see if the chrondata worksheet keys are stored
    if ~isfield(GTSC,'chronData_googleWorkSheetKey')
        bc = cell(length(GTSC),1);
        [GTSC.chronData_googleWorkSheetKey] = bc{:};
    end
    cdgwk={GTSC.chronData_googleWorkSheetKey}';
    if any(cellfun(@isempty,cdgwk)) %see if any are missing keys
       % make sure there are names
        if ~isfield(GTSC,'chronData_chronNumber')
            error('the chron TS metadata must include the chronNumber (which chron object - first number in table name)');
        end
        
      %  figure out table types
        gtsnames = fieldnames(GTSC);
        tni=find(~cellfun(@isempty,(strfind(gtsnames,'TableNumber'))));
        tableType=cell(1,1);
        clear tableNumber
        for tn=1:length(tni)
            gg=find(~cellfun(@isempty,{GTSC.(gtsnames{tni})}));
            usi=strfind(gtsnames{tni},'_');
            tableType(gg,tn)={gtsnames{tni}((usi+6):(end-11))};
            tableNumber(:,tn)={GTSC.(gtsnames{tni})}';
        end
        if size(tableType,2)>1
            if any(sum(~cellfun(@isempty,tableType),2)~=1)
                error('There must be exactly 1 "tableNumber" entry in each row')
            end
            tableType=tableType(~cellfun(@isempty,tableType));
        end
        
        one=repmat({'chron'},length(GTSC),1);
        two={GTSC.chronData_chronNumber}';
        three=tableType;
        four=tableNumber;
        tableName=strcat(one, two, repmat({'-'},length(GTSC),1) ,three,repmat({'Table'},length(GTSC),1), four);
        
        for pie = 1:length(GTSC)
            %match the name to the
            whichCDTsheet = find(strcmp(tableName{pie},wknames));
            cdgwk{pie}=wkKeys{whichCDTsheet};
            display(['Infilling worksheet key ' cdgwk{pie} ' for chronData sheet ' tableName{pie} ])
        end
        [GTSC.chronData_googleWorkSheetKey] = cdgwk{:};
    end
    GTSC=getLiPDGoogleChronData(GTSC);
    
    %collapse the chron TS
    CD=collapseTSChron(GTSC);
         CD=rmfieldsoft(CD,'lipdVersion');

    %CD should only inlcude one file... if it doesn't then thats a problem.
    cnames=fieldnames(CD);
    if length(cnames)>1
        error('there shouldnt be multiple "chronData" ithin one dataset')
    end
    
    %assign the chron structure. %Now operating for version 1.2
        chronData=CD.chronData;
    

    
end
  

    
if isstruct(GTSC)
    for tl=1:length(GTS)
        GTS(tl).chronData=chronData;
    end
end


L=collapseTS1_2(GTS,1);

L = BibtexAuthorString2Cell(L);

L = convertLiPD1_2to1_3(L);

