function [P]=initialize(X)
% takes in the puzzle
% makes the possibilities array
% makes the remaining blanks matrix

P=ones(9,9,9);  % possibilites array
for i=1:9
  for j=1:9
    if X(i,j) ~= 0
      P=update(P,i,j,X(i,j));
    end
  end
end

%R=sum(P,3)~=1;
