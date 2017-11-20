function diffTS = diffTS(miniTS)

%struct array diff...
fn = fieldnames(miniTS);

diffTS = miniTS;
for f = 1:length(fn)
   match = 0;
    this = {miniTS.(fn{f})}';
   
   if all(cellfun(@isempty,this))
       match = 1;
   elseif all(cellfun(@ischar,this))
       if all(strcmp(this{1},this))
           match = 1;
       end
   elseif all(cellfun(@isnumeric,this))
       ls =  cellfun(@length,this);
       if all(ls == 1)
           
           if all(this{1}==cell2mat(this))
               match = 1;
           end
       else
           if all(ls(1)==ls)
               match = 1;
           end
       end
   
   elseif all(cellfun(@iscell,this))
       match = 1; %THIS IS AN ASSUMPTION (BUT PROBABLY REASONABLE)
   end
   
   if match
   diffTS = rmfield(diffTS,fn{f});
   end    
end



