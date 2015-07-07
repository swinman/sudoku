function [X,P]=sudoku(X)
clc

P=initialize(X);
RO_old=9^3;
RO=sum(sum(sum(P,3)-1+(sum(P,3)~=1)));
%RB=sum(sum(sum(P,3)~=1));
while (RO>0 && RO~=RO_old)
  RO_old=RO;
  [X,P]=find_elim(X,P);   % uses possibility array to update X
  P=comp_sets(P);         % updates possibility array
  P=num_forcing(P);       % updates possibility array
  RO=sum(sum(sum(P,3)-1+(sum(P,3)~=1)));
end
X=find_elim(X,P);         % fills in X if need be

RB=sum(sum(sum(P,3)~=1));
RO=sum(sum(sum(P,3)-1+(sum(P,3)~=1)));
if RB==0
  clc, disp('The solution is:'), disp(X)
else
  disp('.'), disp_cur(P,X);
  fprintf('%0.0f Remaining Boxes\n',RB)
  fprintf('%0.0f Remaining Possibilities\n',RO)
  check_ok(P);            % checks that solution can exist
end
