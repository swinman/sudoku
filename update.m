function P=update(P,i,j,x)
% takes in the position (i,j) and value (x) to update and changes P

P(i,j,:)=0;       % excludes all other numbers from box
P(i,:,x)=0;       % blocks repetition of number in row
P(:,j,x)=0;  % blocks repetition of number in column
% blocks repitition of number in quadrant
P(i-rem(i-1,3):i+2-rem(i-1,3),j-rem(j-1,3):j+2-rem(j-1,3),x)=0;
P(i,j,x)=1;  % re-set value

