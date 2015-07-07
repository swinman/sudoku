function disp_cur(P,X)
% takes in the probablity matrix, current solution & remainder matrix
% displays the current possibilities

empty=find(sum(P,3)~=1);
for n=1:length(empty)
	r=rem(empty(n)-1,9)+1;
  c=fix((empty(n)-1)/9)+1;
  x=find(P(r,c,:));
  for m=1:length(x)
    X(r,c)=X(r,c)+10^(m-1)*x(length(x)-m+1);
  end
end
disp(X)

