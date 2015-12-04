function data=getRowFromXML(con)
test=xmlread(con.getInputStream());
allListitems=test.getElementsByTagName('entry');
clear data
data=cell(1,1);
for k = 0:allListitems.getLength-1
   t = allListitems.item(k);
   t2=t.getChildNodes;
   cL=t2.getLength;
%    %safer but slower? method
%    for c=0:(cL-1)
%        t3=t2.item(c);
%        if strcmp('content',t3.getNodeName)
%            almost=t3.item(0);
%            gotIt=char(almost.getData);
%            
%            data{b,1}=gotIt;
%            b=b+1;
%        end
%    end


%faster method, but might break
if cL==8
    tt=t2.item(3);
    almost=tt.item(0);
    gotIt=char(almost.getData);   
    col=letter2col(regexprep(gotIt,'[^A-Z]',''));
    
    t3=t2.item(4);
    almost=t3.item(0);
    gotIt=char(almost.getData);   
    data{1,col}=gotIt;


end

end
end
function number=letter2col(letter)
if length(letter)>1
    error('not set up for rows > 26 yet')
end
alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ';
number=strfind(alphabet,letter);
end

