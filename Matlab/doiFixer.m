function [DOIout,citeOut] = doiFixer(DOIin)

DOIout = cell(size(DOIin));
citeOut = DOIout;
for i = 1:length(DOIin)
    toFix=DOIin{i};
   dStart = min(strfind(toFix,'10.'));
   if length(dStart)==1
       DOIout{i} = toFix(dStart:end);
   else
       citeOut{i} = toFix;
   end
end

