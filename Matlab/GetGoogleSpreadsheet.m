function [result, result2]= GetGoogleSpreadsheet(DOCID)
% result = GetGoogleSpreadsheet(DOCID)
% Download a google spreadsheet as csv and import into a Matlab cell array.
%
% [DOCID] see the value after 'key=' in your spreadsheet's url
%           e.g. '0AmQ013fj5234gSXFAWLK1REgwRW02hsd3c'
%
% [result] cell array of the the values in the spreadsheet
%
% IMPORTANT: The spreadsheet must be shared with the "anyone with the link" option
%
% This has no error handling and has not been extensively tested.
% Please report issues on Matlab FX.
%
% DM, Jan 2013
%
%NM: Edied parseCsv to deal with carriage returns in cells. 15/6/16


loginURL = 'https://www.google.com'; 
csvURL = ['https://docs.google.com/spreadsheet/ccc?key=' DOCID '&output=csv&pref=2'];

%Step 1: go to google.com to collect some cookies
cookieManager = java.net.CookieManager([], java.net.CookiePolicy.ACCEPT_ALL);
java.net.CookieHandler.setDefault(cookieManager);
handler = sun.net.www.protocol.https.Handler;
connection = java.net.URL([],loginURL,handler).openConnection();
connection.getInputStream();

%Step 2: go to the spreadsheet export url and download the csv
connection2 = java.net.URL([],csvURL,handler).openConnection();
result = connection2.getInputStream();
result2 = char(readstream(result));



%Step 3: convert the csv to a cell array
result = parseCsv(result2);

end

function dataOut = parseCsv(data)
    %how many columns in first row?
    data1 = textscan(data,'%q','whitespace','\n');
    row1 = data1{1}(1);
    nCol = length(strfind(row1{1},','))+1;

% splits data into individual lines
data2 = textscan(data,repmat('%q',1,nCol),'whitespace','\n','Delimiter',',');
%data = data{1};
nRow = max(cellfun(@length,data2));
dataOut = cell(nRow,nCol);
for ii=1:length(data2)
   %for each line, split the string into its comma-delimited units
   %the '%q' format deals with the "quoting" convention appropriately.
   dataOut(1:length(data2{1,ii}),ii) = data2{1,ii};
end

end

function out = readstream(inStream)
%READSTREAM Read all bytes from stream to uint8
%From: http://stackoverflow.com/a/1323535

import com.mathworks.mlwidgets.io.InterruptibleStreamCopier;
byteStream = java.io.ByteArrayOutputStream();
isc = InterruptibleStreamCopier.getInterruptibleStreamCopier();
isc.copyStream(inStream, byteStream);
inStream.close();
byteStream.close();
%out = typecast(byteStream.toByteArray', 'uint8'); 
out = native2unicode(typecast(byteStream.toByteArray', 'uint8')); 

end
