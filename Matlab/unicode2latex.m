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

%first look for longer strings
%which strings are longer than 1
lccshort = latexCharConv(cellfun(@length,latexCharConv(:,1))>1,:);

for j=1:size(lccshort,1)
    sin = strfind(out, lccshort{j,1});
    for i=length(sin):-1:1
        sini = sin(i);
        len = length(lccshort{j,1});
        if sini>1
            out = [out(1:(sini-1)) latexCharConv{j,2} out((sini+len):end)];
        else
            out = [latexCharConv{j,2} out((sini+len):end)];
            
        end
    end
end


for i=length(out):-1:1
    ind=find(strcmp(out(i),latexCharConv(:,1)));
    if ~isempty(ind)
        if i>1
            out = [out(1:(i-1)) latexCharConv{ind,2} out((i+1):end)];
        else
            out = [latexCharConv{ind,2} out((i+1):end)];
            
        end
    end
    
end


