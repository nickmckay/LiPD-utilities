function I=readLiPDPub1_0(I)

%pull DOI to front
if ~iscell(I.pub)
    clear pu
    pu{1}=I.pub;
    I.pub=pu;
end
for pp=1:length(I.pub)
    if isfield(I.pub{pp},'identifier')
        if strcmpi(I.pub{pp}.identifier{1,1}.type,'doi')
            if isfield(I.pub{pp}.identifier{1,1},'id')
            I.pub{pp}.DOI=I.pub{pp}.identifier{1,1}.id;
            end
        end
    end
    %deal with updated way to store authors (bibJSON standard)
    %ultimately, they all should be this way
    if isfield(I.pub{pp},'author')
        if iscell(I.pub{pp}.author)
            if isstruct(I.pub{pp}.author{1})
                newAuthor=cell(1,length(I.pub{pp}.author));
                for nA=1:length(cell(1,length(I.pub{pp}.author)))
                    newAuthor{nA}= I.pub{pp}.author{nA}.name;
                end
                I.pub{pp}.author=newAuthor;
            end
        end
    end
    
end