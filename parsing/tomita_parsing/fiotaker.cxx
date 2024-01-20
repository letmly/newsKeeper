#encoding "utf-8"
#GRAMMAR_ROOT PERS
PERS -> (AnyWord*) Word<kwset=person> interp (Name.personName) (AnyWord*);
//MENT -> PERS interp(Name.personMention);