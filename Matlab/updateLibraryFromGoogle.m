%update LiPD library from google

%cd ~/Dropbox/LiPD/library/

l=dir('*.lpd');
l={l.name}';

for i=1:length(l)
    name=l{i};
    L=readLiPD(name);
L=updateLiPDfromGoogle(L);
    
%remove old file before writing new one.
delete(name);

writeLiPD(L);
    

end