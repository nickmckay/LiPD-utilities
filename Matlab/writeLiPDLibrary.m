function writeLiPDLibrary(Dout,overwrite,libDir)
%write LiPD library
if nargin < 3
    libDir=uigetdir;
end

if nargin<2
    overwrite=0;
end

%make the directory if you need to
if ~isdir(libDir)
    mkdir(libDir);
end
cd(libDir)

%clear out the folder if it exists
if overwrite
    sure = input(['are you sure you want to delete all the lipd files in ' libDir]);
    if strncmpi('y',sure,1)
        delete('*.lpd')
    end
end

dnames=fieldnames(Dout);
for d=1:length(dnames)
    cd(libDir)
    try
    writeLiPD(Dout.(dnames{d}));
    catch ME
        warning([dnames{d} ' encountered errors and didnt write out']);
        proceed = input('Do you want to proceed?')
            if strncmpi('y',proceed,1)
            else
                error('You chose to stop')
            end
    end
end