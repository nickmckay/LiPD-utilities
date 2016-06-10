%set up LiPD on local computer...
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


updateNameConverterFromGoogle

save LiPDUtilitiesPreferences.mat githubPath
