cd ~/Dropbox/Pages2kPhase2/LibraryNew/ %path to load


l=dir('*.lpd');
l={l.name}';
clear D
for i=1:length(l)
    name=l{i};
    %L=readLiPD(name);
    
   D.(matlab.lang.makeValidName(   name(1:(end-4))))=readLiPD(name);

end

D=validateLiPD(D);

TS=extractTimeseriesLiPD(D);
TS=structord(TS);
