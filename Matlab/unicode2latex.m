function out = unicode2latex(string)

%load in conversion table
load latexCharConv

if iscell(string)
    string=cell2str(string);
end

if ~ischar(string)
    error('requires string input');
end
out = string;
for i=length(string):-1:1
   ind=find(strcmp(string(i),latexCharConv(:,1)));
   if ~isempty(ind)
       if i>1
           out = [out(1:(i-1)) latexCharConv{ind,2} out((i+1):end)];
       else
           out = [latexCharConv{ind,2} out((i+1):end)];

       end
   end
    
end
    

