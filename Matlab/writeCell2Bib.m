function writeCell2Bib(C,filename)

if nargin<2
    [file , pathname] = uiputfile('.bib');
    filename=[pathname file];
end

fid = fopen(filename,'w');

header = {'%% This BibTeX bibliography file was created by writeCell2Bib.m',
        '%% https://github.com/nickmckay/LiPD-utilities/tree/master/Matlab/writeCell2Bib.m',
        ' ',
        ' ',
        ['%% created on ' datestr(now) ],
        ' '};
        
for i=1:length(header)
fprintf(fid,'%s\n',header{i});
end


for i = 1:length(C)
    c=C{i};
   for j = 1 :length(c)
      fprintf(fid,'%s\n',c{j});
   end
   fprintf(fid,'%s\n',' ');

end
fclose(fid)

