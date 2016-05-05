function D = readLiPDLibrary(direc)

if nargin<1
    direc = uigetdir;
end

cd(direc)

lpds = dir('*.lpd')
for l=1:length(lpds)
    L = readLiPD(lpds(l).name);
    if ~isfield(L,'dataSetName')
        L.dataSetName = matlab.lang.makeValidName(lpds(l).name(1:end-4));
    end
    D.(L.dataSetName)=L;
end

