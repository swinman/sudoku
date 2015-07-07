%% test
clear
X=[0 2 0 0 3 0 0 4 0;6 0 0 0 0 0 0 0 3;0 0 4 0 0 0 5 0 0;...
   0 0 0 8 0 6 0 0 0;8 0 0 0 1 0 0 0 6;0 0 0 7 0 5 0 0 0;...
   0 0 7 0 0 0 6 0 0;4 0 0 0 0 0 0 0 8;0 3 0 0 4 0 0 2 0];
%X=X';

[X,P]=sudoku(X);

%% test a solution
X_real=X; P_real=P;
max_test=max(max(sum(P,3)));

tc=find(sum(P,3)==max_test);
r=rem(tc(1)-1,9)+1; c=fix((tc(1)-1)/9)+1;

x=find(P(r,c,:));
OK=ones(1,max_test);
CPLT=zeros(1,max_test);
XP=zeros(9,9,max_test);
for i=1:max_test
  X_test=X_real;
  X_test(r,c)=x(i);
  [X_test,P]=sudoku(X_test);
  OK(i)=check_ok(P);
  if sum(sum(X_test==0))==0, CPLT(i)=1; end
  XP(:,:,i)=X_test;
end


clc, fprintf('%0.0f Potential Solutions\n',sum(OK))
fprintf('%0.0f Total Complete Solutions\n',OK*CPLT')

solmat=find(OK);
for i=1:length(solmat)
  disp(XP(:,:,solmat(i)))
end

if length(solmat)==1
  X=XP(:,:,solmat);
	P=initialize(X);
end

%% solve by eliminations (one iteration of sudoku.m)
[X,P]=find_elim(X,P);   % uses possibility array to update X
P=comp_sets(P);         % updates possibility array
P=num_forcing(P);       % updates possibility array

RO=sum(sum(sum(P,3)-1+(sum(P,3)~=1)));
RB=sum(sum(sum(P,3)~=1));

if RB==0
  clc, disp('The solution is:'), disp(X)
else
  disp('.'), disp_cur(P,X);
  fprintf('%0.0f Remaining Boxes\n',RB)
  fprintf('%0.0f Remaining Possibilities\n',RO)
  check_ok(P);            % checks that solution can exist
end


%% remainders
clc
Rnum=permute(sum(sum(P)-1+(sum(P)~=1)),[1 3 2]);
fprintf('%0.0f Finished Numbers, remainder per number:\n',sum(Rnum==0))
disp(Rnum)

Rcol=sum(sum(P,3)~=1);
fprintf('%0.0f Finished Columns, remainder per column:\n',sum(Rcol==0))
disp(Rcol)

Rrow=sum(sum(P,3)~=1,2)';
fprintf('%0.0f Finished Rows, remainder per row:\n',sum(Rrow==0))
disp(Rrow)

Rbox=1:9; remainder=sum(P,3)~=1;
for q=1:9
  i=fix((q-1)/3)*3+1; j=rem(q-1,3)*3+1;
  Rbox(q)=sum(sum(remainder(i:i+2,j:j+2)));
end
fprintf('%0.0f Finished Quads, remainder per quad:\n',sum(Rbox==0))
disp(Rbox)

fprintf('%0.0f Remaining Boxes\n',sum(sum(sum(P,3)~=1)))
fprintf('%0.0f Remaining Options\n',sum(sum(sum(P,3)-1+(sum(P,3)~=1))))

%% display possibilities for a spot
pos=find(P(4,9,:))';
disp(pos)

%%
X_gold=X; P_gold=P;
%%
clc
X=X_gold; P=P_gold;

x=9;  row=4;  col=5;

X(row,col)=x; P=update(P,row,col,x);
disp_cur(P,X);    % displays current solution matrix


