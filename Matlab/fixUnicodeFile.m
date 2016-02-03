function fixUnicodeFile(file,newfile)
%go through a text file and replace unicode with good characters
fclose('all');
if nargin<2
newfile='tempFile.txt';
end
fidn=fopen(newfile,'a');
fid=fopen(file);
t=1;
while 1
    line=fgetl(fid);
    if line==-1 
        break
    end
    newLine=fixUnicodeStr(line);
    fprintf(fidn,'%s\n',newLine);
    t=t+1;
end
fclose(fid);
fclose(fidn);

if nargin<2%copy new file to old file, then delete new file
    if isunix
        system(['cp ' newfile ' ' file]);
        system(['rm ' newfile]);
    else
        error('file replacement not set up for windows yet')
    end
end
        
        
