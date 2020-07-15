function D = readLiPD(path)


%ui selection
if nargin<1
    answer = input('Do you want to load a single file (''s'') or a directory (''d'')?)');
    if strncmpi(answer,'d',1)
        lpdpath = uigetdir;
        multiFlag = 1;
    else
        [lpdfile, lpdpath] = uigetfile('.lpd');
        lpdname = [lpdpath lpdfile];
        multiFlag = 0;
    end
else %parse the name to look for .lpd
    if isdir(path)
        %then it's a path
        lpdpath = path;
        multiFlag = 1;
    else
        %then it's a file
        lpdname = path;
        multiFlag = 0;
    end
end

if multiFlag
    cd(lpdpath)
    
    lpds = dir('*.lpd');
    for l=1:length(lpds)
        try
            L = readLiPDFile(lpds(l).name);
            
            if ~isfield(L,'dataSetName')
                L.dataSetName = lpds(l).name(1:end-4);
            end
            D.(makeValidName(L.dataSetName))=L;
        catch ME
            warning(['couldnt read ' lpds(l).name])
        end
       
    end
    
else
    D = readLiPDFile(lpdname);
end







