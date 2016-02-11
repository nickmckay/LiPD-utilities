%update LiPD library from google
%store MD5 sum?

cd ~/Dropbox/LiPD/library/

l=dir('*.lpd');
l={l.name}';
lNoExt=cellfun(@(x)x(1:end-4),l,'UniformOutput',0);

%update
checkGoogleTokens;

if 1
%find which googleLiPDs have been recently updated.
list=getSpreadsheetList(aTokenSpreadsheet);

updateDate=now-(4/24)+7/24;%acount for zulu time
recent=find((cell2mat({list.updatedNumeric}')-updateDate)>0);

n=1;
clear toUpdate
for u=1:length(recent)
   f=find( strcmp(list(recent(u)).spreadsheetTitle,lNoExt));
   if length(f)==1
    toUpdate(n)=f;
    n=n+1;
   end
end

else
    toUpdate=1:length(l);
end
%%
for i=1:length(toUpdate)
    name=l{toUpdate(i)};
    L=readLiPD(name);
L=updateLiPDfromGoogle(L);
    
%remove old file before writing new one.
delete(name);

writeLiPD(L);
    

end

%clear 
%run('~/Dropbox/Pages2kPhase2/loadLiPDLibrary.m')