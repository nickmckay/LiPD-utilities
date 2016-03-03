function c=stringifyCells(c)
%make all cell entries strings

nr=size(c,1);
nc=size(c,2);

for i=1:nr
    for j=1:nc
        if ~ischar(c{i,j})
            
            if isnumeric(c{i,j})
                c{i,j}=num2str(c{i,j});
            elseif isstruct(c{i,j})
                c{i,j}='nested data, can''t represent here';
            elseif iscell(c{i,j})
                inside=c{i,j}{1};
                if ~isstruct(inside)
                    c{i,j}=cell2str(c{i,j});
                elseif isstruct(inside)
                    c{i,j}=cell2str(struct2cell(inside));
                end
            end
        end
        %         if ~isstr(c{i,j})
        %             error([c{i,j} ' is not a string'])
        %         end
        dum=c{i,j};
        if min(size(dum))>1
            dum=reshape([dum repmat(';',size(dum,1),1)]',1,[]);
        end
        %save dum.mat  dum
%         if isnumeric( c{i,j})
%             c{i,j}=num2str(c{i,j});
%         end
        c{i,j}=regexprep(dum,'[''}{]','');
    end
end
