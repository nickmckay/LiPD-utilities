function wget_cmmnd=ml_wget(ofile,url)
% wget_cmmnd=ml_wget(ofile,url)

wget_flags=' --passive-ftp ';
wget_cmmnd=['!/usr/local/bin/wget' wget_flags '-O ' ofile ' "' url '"'];
disp(wget_cmmnd)
eval(wget_cmmnd)
