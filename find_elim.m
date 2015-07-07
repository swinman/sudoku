function [X,P]=find_elim(X,P)
% performs simple elimination steps to obtain solution
% all steps are direct (possibilities are only removed because of adjacent
% numbers), and values are found by either there being no other possible
% values for the space, or there being no other possible positions for the
% number


% check when only one number can satisfy a box
chk=find(sum(P,3)==1);
for n=1:length(chk), j=fix((chk(n)-1)/9)+1; i=rem(chk(n)-1,9)+1; 
  for x=1:9, if P(i,j,x)==1 
    X(i,j)=x; P=update(P,i,j,x); 
%    fprintf('%0.0f goes in row %0.0f, col %0.0f\n',x,i,j)
  end, end
end

% check when a number can't fit anywhere else in a row, column or box
row_val=zeros(9,9); rvk=row_val;
col_val=zeros(9,9); cvk=col_val;
box_val=zeros(9,9); bvk=box_val;
for x=1:9
  row_val(x,:)=sum(P(:,:,x),2);   % i (down) is num, j (across) is the row
  col_val(x,:)=sum(P(:,:,x),1)';  % i (down) is num, j (across) is the row
  rvk(x,:)=sum(X==x,2)';    % known row values
  cvk(x,:)=sum(X==x);       % known col values
  for q=1:9
    i=fix((q-1)/3)*3+1; j=rem(q-1,3)*3+1;
    box_val(x,q)=sum(sum(P(i:i+2,j:j+2,x)));
    bvk(x,q)=sum(sum(X(i:i+2,j:j+2)==x));
  end
end

%
rv=(row_val==1)+(row_val==2)*2+(row_val==3)*3;
cv=(col_val==1)+(col_val==2)*2+(col_val==3)*3;
bv=(box_val==1)+(box_val==2)*2+(box_val==3)*3;
% finds new singular values
rvx=find((rv==1)-rvk); cvx=find((cv==1)-cvk); bvx=find((bv==1)-bvk);
% need to find new duplicate values

for n=1:length(rvx), i=fix((rvx(n)-1)/9)+1; x=rem(rvx(n)-1,9)+1;
  for j=1:9, if P(i,j,x) == 1
    X(i,j)=x; P=update(P,i,j,x);
%    fprintf('%0.0f goes in row %0.0f, col %0.0f\n',x,i,j)  
  end, end
end

for n=1:length(cvx), j=fix((cvx(n)-1)/9)+1; x=rem(cvx(n)-1,9)+1;
  for i=1:9, if P(i,j,x) == 1
    X(i,j)=x; P=update(P,i,j,x); 
%    fprintf('%0.0f goes in row %0.0f, col %0.0f\n',x,i,j)  
  end, end
end

for n=1:length(bvx), q=fix((bvx(n)-1)/9)+1; x=rem(bvx(n)-1,9)+1;
  for i=fix((q-1)/3)*3+1:fix((q-1)/3)*3+3
  for j=rem(q-1,3)*3+1:rem(q-1,3)*3+3, if P(i,j,x) == 1
    X(i,j)=x; P=update(P,i,j,x); 
%    fprintf('%0.0f goes in row %0.0f, col %0.0f\n',x,i,j)
  end, end, end
end

