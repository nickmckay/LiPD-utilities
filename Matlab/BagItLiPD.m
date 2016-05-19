folders=dir;
folders={folders(find(cell2mat({folders.isdir}))).name}';
folders=folders(find(~strcmp('.',cellfun(@unique,folders,'UniformOutput',0))));

for i=i:length(folders)
    cd([folders{i}])
    if length(dir('data'))==0 %see if it's already been bagged
        cd ..
        system(['/Library/Frameworks/Python.framework/Versions/3.4/bin/bagit.py "' folders{i} '"']);
    else
    cd ..
    end
    zip([folders{i}], folders{i});
    movefile([folders{i} '.zip'],[folders{i} '.lpd']);
    delete([folders{i} '.zip']);
end