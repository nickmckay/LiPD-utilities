2011/04/27
This set of matlab functions will allow creating
Google spreadsheets, adding worksheets to them, modifying the
worksheets, and placing data in them. The delete worksheet
function works intermittently so far (the DELETE request throws
400/Bad request sometimes).

Please see Matlab2GoogTest.m for sample usage (you'll need to
enter your gmail username/password).

Please note that you need to have urlreadwrite.m (unmodified as
available in the Matlab distribution in
MATLABROOT/toolbox/matlab/iofun/private/urlreadwrite.m) on your
path.

This was very much inspired by submission of Ofir Bibi (Create
Google Calendar event with SMS and Email notification, File ID:
#25698).

2011/6/20
The Google login box was inspired by submission of Matt Fig (41
Complete GUI Examples, File ID: #24861). Some of the code was
somewhat simplified, there is a new function, getWorksheetCell,
that reads both the cell value and the forumula. editWorksheetCell
supports entering formulas as string (see Google Spreadsheet
API for examples).

2015/08/24
Updated to new Google Oauth2. Application client id and client secret
must be obtained from Google developer console (get oauth2 client id and 
use Other for application type). Google login is not required anymore. You use a separate
browser to get client id and client secret then also use the browser to allow access to Google Drive API
and Google Sheets API. See the code for storing the access and refresh tokens in a mat file.
Updated requests to use new authorization. Unlike previous version to create a new spreadsheet 
you need to upload an existing MSExcel/LibreOffice spreadsheet that gets converted (so you can upload 
an empty one or one with existing data to use later on).
There's still room for improvement/making things more robust. Feedback is appreciated.

2015/09/06
Following Scott's editWorksheetRow function in the comments the following two functions were introduced:
editWorksheetRow (slightly modified version of the one Scott submitted in comments) and editWorksheetColumn
