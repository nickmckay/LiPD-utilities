function uTS=convertNamesTS(TS,field)
uTS = TS;
toCon={TS.(field)}';


[newNames,changed] = convertName(field,toCon);
wc = find(changed);

%append a note about the change to the ones that changed.
notes = {TS.paleoData_notes}';
newnote = strcat(repmat({['; ' field ' changed - was originally ']},length(notes),1), toCon);
append = repmat({''},length(notes),1);
append(wc,1)=newnote(wc,1);
newNotes = strcat(notes,append);

[uTS.paleoData_notes] = newNotes{:};
[uTS.(field)] =  newNames{:};
