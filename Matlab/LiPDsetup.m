%set up LiPD on local computer...
display('Where is the LiPD-Utilities/matlab folder on your computer?')
githubPath=uigetdir('Where is the LiPD-Utilities/matlab folder on your computer?');
cd(githubPath)

addpath(genpath(githubPath))

display('OK, Ive added that path and its subfolders to your path')
savepath

tsidCell=GetGoogleSpreadsheet('15IsdiTf790BRPXVL7GsW_j7wrQDHIEB9NmFI0lqqMuY');
tsidCell=tsidCell(2:end,:);
lastSync=now;
save tsidCell.mat tsidCell lastSync

goog=GetGoogleSpreadsheet('1C135kP-SRRGO331v9d8fqJfa3ydmkG2QQ5tiXEHj5us' ) ;
save localRenameTS.mat goog lastSync
save LiPDUtilitiesPreferences.mat githubPath

%setup bagit for mac. Deduce python version
if ismac
    out = dir('/Library/Frameworks/Python.framework/Versions');
    pyVers = out(end).name;
    
    buffer = fileread([githubPath '/bagit.py']) ;
 buffer = regexprep(buffer, 'Versions/3.4/bin/', ['Versions/' pyVers '/bin/']) ;
 fid = fopen([githubPath '/bagit.py'], 'w') ;
 fwrite(fid, buffer) ;
 fclose(fid) ;
    
end



updateNameConverterFromGoogle

save LiPDUtilitiesPreferences.mat githubPath
