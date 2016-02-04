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