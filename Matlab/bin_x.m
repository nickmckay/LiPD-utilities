function [bin_mean, BinTime, sem] =  bin_x(Xtime,X,bins,edgestring);
%[bin_mean, BinTime, standard error of the mean] =  bin_x(Xtime,X,bins);

if length(Xtime) ~= size(X,1)
    error('age and value vectors must be the same length')
end
    
binstep = bins(2)-bins(1);
inclstart=0;
if nargin>3
if strcmp(edgestring,'start')
    inclstart=1;
end
end

for i = 1:length(bins)-1
    if inclstart
    q = find(Xtime >= bins(i) & Xtime<bins(i+1));
    else
    q = find(Xtime > bins(i) & Xtime<=bins(i+1));
    end
    bin_mean(i,:) = [nanmean(X(q,:))];
    %bin_sum(i,:)  = [nansum(X(q,:),1)];
    BinTime(i,1)= nanmean(Xtime(q));
%     if length(find(~isnan(X(q,:)))) == 1
%         sem(i,:)=NaN;
%     else
%     sem(i,:) = std(X(q,:))./sqrt(length(find(~isnan(X(q,:)))));
%     end
end
end
