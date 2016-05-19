function LiPDStruct = writeLiPDPub(LiPDStruct)
%%%%%START PUB SECTION %%%%%%%%%%
for dd=1:length(LiPDStruct.pub)
    if isfield(LiPDStruct.pub{dd},'DOI')
        if iscell(LiPDStruct.pub{dd}.DOI)
            LiPDStruct.pub{dd}.DOI=LiPDStruct.pub{dd}.DOI{1};
        end
        doistring=strtrim(LiPDStruct.pub{dd}.DOI);
        dh=strfind(doistring,'doi:');
        if ~isempty(dh)                
            doistring=doistring(setdiff(1:length(doistring),dh));
        end
        LiPDStruct.pub{dd}.identifier{1,1}.type='doi';
        LiPDStruct.pub{dd}.identifier{1,1}.id=doistring;
        LiPDStruct.pub{dd}.identifier{1,1}.url=['http://dx.doi.org/' doistring];
        LiPDStruct.pub{dd}=rmfield(LiPDStruct.pub{dd},'DOI');
    end
end
%%%%%END PUB SECTION %%%%%%%%%%
