function out = inThisCompilation(TS,compName,compVers)

%get all the names in the TS
allNames = fieldnames(TS);

%get the compilation names
allComps = allNames(~cellfun(@isempty,regexpi(allNames,'inCompilationBeta[0-9]+_compilationName')));


%get the compilation versions
allVers = allNames(~cellfun(@isempty,regexpi(allNames,'inCompilationBeta[0-9]+_compilationVersion')));

if length(allComps) == 0
 out = nan(length(TS),1);
end


allCompNames = cell(length(allComps),1);
allCompVersions = allCompNames;

%get all teh data
  for i = 1:length(allComps)
  allCompNames{i} = {TS.(allComps{i})}';
  allCompVersions{i} = {TS.(allVers{i})}';
  end
  
  compCheck = nan(length(allCompNames{1}),length(allComps));
  
  %check across all inComps
  for i = 1:length(allComps)
     compCheck(:,i) = checkFun(compName,compVers,allCompNames{i},allCompVersions{i});
  end
  
  out = sum(compCheck,2) > 0;
  
end
  

  function bothMatch = checkFun(cn,cv,compName,compVers)
  bothMatch = strcmp(cn,compName) & cellfun(@(x,y) any(strcmp(x,y)),repmat({cv},length(compVers),1),compVers);
  %incn = find(isnan(cn));
  %bothMatch(incn) = NaN;
  end
  
  
  
  
  
  
  
  