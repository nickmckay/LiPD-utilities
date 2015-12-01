allListitems=test.getElementsByTagName('entry');


for k = 0:allListitems.getLength-1
   thisListitem = allListitems.item(k);
   t=thisListitem.getElementsByTagName('content');
   
   
   
   % Get the label element. In this file, each
   % listitem contains only one label.
   thisList = thisListitem.getElementsByTagName('entry');
   thisElement = thisListitem.item(0);
% 
%    % Check whether this is the label you want.
%    % The text is in the first child node.
%    if strcmp(thisElement.getFirstChild.getData, 'content')
%        thisList = thisListitem.getElementsByTagName('callback');
%        thisElement = thisList.item(0);
%        findCbk = char(thisElement.getFirstChild.getData);
%        break;
%    end
child=thisElement.getFirstChild.getData;
% if isnumeric(thisElement)
%     test2(k+1)=thisElement.getFirstChild.getData;
% end
end