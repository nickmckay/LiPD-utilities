function medRes = calculateMedianResolutionTS(TS,yearCol,minYear,maxYear)

if nargin<2
    yearCol = 'year'
end
if nargin<4 
    maxYear = Inf;
end
if nargin<3
   minYear = -Inf;
end
    

age = {TS.(yearCol)};

goodAge = cellfun(@(x) restrictYear(x,minYear,maxYear),age,'UniformOutput',0);

medRes = cellfun(@(x) nanmedian(abs(diff(x))), goodAge);


end

function year = restrictYear(year,minYear,maxYear)
    good = find(year>= min([minYear maxYear]) & year<= max([minYear maxYear])); 
    year = year(good);
    

end



