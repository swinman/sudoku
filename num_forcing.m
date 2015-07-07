function [P]=num_forcing(P)
% takes in and updates probability array
% elimination of row/col bc of req for a box, or elim in box from r/c req
% when a number is only possible in a single row or column in a quad, the
% number can't be in that row / column in an adjacent quad
% when a number is only possible in one quad of a row, the number can't be
% in a different row of that quad

Pcol=[sum(P(1:3,:,:));sum(P(4:6,:,:));sum(P(7:9,:,:))];
Prow=[sum(P(:,1:3,:),2) sum(P(:,4:6,:),2) sum(P(:,7:9,:),2)];
clear hlpr hlpc hlbr hlbc

% check for times when there is only 1 column that works in a quad
pc=[xor(Pcol(:,1,:),xor(Pcol(:,2,:),Pcol(:,3,:)))...
  xor(Pcol(:,4,:),xor(Pcol(:,5,:),Pcol(:,6,:)))...
  xor(Pcol(:,7,:),xor(Pcol(:,8,:),Pcol(:,9,:)))];
pc2=[~(Pcol(:,1,:)&(Pcol(:,2,:)&(Pcol(:,3,:))))...
  ~(Pcol(:,4,:)&Pcol(:,5,:)&Pcol(:,6,:))...
  ~(Pcol(:,7,:)&Pcol(:,8,:)&Pcol(:,9,:))];
pc=pc.*pc2; 

%check when other columns will get deleted, otherwise usless step
hlpc(1,:,:)=Pcol(1,:,:)&(Pcol(2,:,:)|Pcol(3,:,:));
hlpc(2,:,:)=Pcol(2,:,:)&(Pcol(1,:,:)|Pcol(3,:,:));
hlpc(3,:,:)=Pcol(3,:,:)&(Pcol(1,:,:)|Pcol(2,:,:));
hlpc=[sum(hlpc(:,1:3,:),2) sum(hlpc(:,4:6,:),2) sum(hlpc(:,7:9,:),2)].*pc;

loc=find(hlpc);
for n=1:length(loc)
  x=fix((loc(n)-1)/9)+1;  % the number to remove
  a=rem(loc(n)-1,9)+1;    % transpose of the quadrant
  r=rem(a-1,3)+1;         % the row (of 3 in Pcol) to check for the place
  c1=fix((a-1)/3)*3+1;    % the col to start checking for the place
  c=fix((a-1)/3)*3+find(Pcol(r,c1:c1+2,x)); % the column to remove
  t=zeros(9,1); t(((r-1)*3+1):((r-1)*3+3))=1; P(:,c,x)=P(:,c,x)&t;
end

pr=[xor(Prow(1,:,:),xor(Prow(2,:,:),Prow(3,:,:)));...
  xor(Prow(4,:,:),xor(Prow(5,:,:),Prow(6,:,:)));...
  xor(Prow(7,:,:),xor(Prow(8,:,:),Prow(9,:,:)))];
pr2=[~(Prow(1,:,:)&(Prow(2,:,:)&(Prow(3,:,:))));...
  ~(Prow(4,:,:)&Prow(5,:,:)&Prow(6,:,:));...
  ~(Prow(7,:,:)&Prow(8,:,:)&Prow(9,:,:))];
pr=pr.*pr2;

hlpr(:,1,:)=Prow(:,1,:)&(Prow(:,2,:)|Prow(:,3,:));
hlpr(:,2,:)=Prow(:,2,:)&(Prow(:,1,:)|Prow(:,3,:));
hlpr(:,3,:)=Prow(:,3,:)&(Prow(:,1,:)|Prow(:,2,:));
hlpr=[sum(hlpr(1:3,:,:));sum(hlpr(4:6,:,:));sum(hlpr(7:9,:,:))].*pr;

lor=find(hlpr);
for n=1:length(lor)
  x=fix((lor(n)-1)/9)+1;  % the number to remove
  a=rem(lor(n)-1,9)+1;    % the transpose of the quadrant
  c=fix((a-1)/3)+1;      % the col (of 3 in Prow) to check for the place
  r1=rem(a-1,3)*3+1;         % the row to start checking for the place
  r=rem(a-1,3)*3+find(Prow(r1:r1+2,c,x)); % the column to remove
  t=zeros(1,9); t(((c-1)*3+1):((c-1)*3+3))=1; P(r,:,x)=P(r,:,x)&t;
end

% check times when all of a value from a col appear in 1 box
pbc=xor(Pcol(1,:,:),xor(Pcol(2,:,:),Pcol(3,:,:))).*...
  ~(Pcol(1,:,:)&(Pcol(2,:,:)&(Pcol(3,:,:))));

% check when other values in the box will be deleted as a result
hlbc=[Pcol(:,1,:)&(Pcol(:,2,:)|Pcol(:,3,:))...
  Pcol(:,2,:)&(Pcol(:,1,:)|Pcol(:,3,:))...
  Pcol(:,3,:)&(Pcol(:,1,:)|Pcol(:,2,:))...
  Pcol(:,4,:)&(Pcol(:,5,:)|Pcol(:,6,:))...
  Pcol(:,5,:)&(Pcol(:,4,:)|Pcol(:,6,:))...
  Pcol(:,6,:)&(Pcol(:,4,:)|Pcol(:,5,:))...
  Pcol(:,7,:)&(Pcol(:,8,:)|Pcol(:,9,:))...
  Pcol(:,8,:)&(Pcol(:,7,:)|Pcol(:,9,:))...
  Pcol(:,9,:)&(Pcol(:,7,:)|Pcol(:,8,:))];
hlbc=sum(hlbc).*pbc;

lbc=find(hlbc);
for n=1:length(lbc)
  x=fix((lbc(n)-1)/9)+1;  % the number to remove
  c=rem(lbc(n)-1,9)+1;    % the column to keep
  r=find(Pcol(:,c,x));    % the row in Pcol
  t=zeros(3); t(:,rem(c-1,3)+1)=1;
  P((r-1)*3+1:(r-1)*3+3,c-rem(c-1,3):c-rem(c-1,3)+2,x)=...
    P((r-1)*3+1:(r-1)*3+3,c-rem(c-1,3):c-rem(c-1,3)+2,x)&t;
end

% check times when all of a value from a row appear in 1 box
pbr=xor(Prow(:,1,:),xor(Prow(:,2,:),Prow(:,3,:))).*...
  ~(Prow(:,1,:)&(Prow(:,2,:)&(Prow(:,3,:))));

hlbr=[Prow(1,:,:)&(Prow(2,:,:)|Prow(3,:,:));...
  Prow(2,:,:)&(Prow(1,:,:)|Prow(3,:,:));...
  Prow(3,:,:)&(Prow(1,:,:)|Prow(2,:,:));...
  Prow(4,:,:)&(Prow(5,:,:)|Prow(6,:,:));...
  Prow(5,:,:)&(Prow(4,:,:)|Prow(6,:,:));...
  Prow(6,:,:)&(Prow(4,:,:)|Prow(5,:,:));...
  Prow(7,:,:)&(Prow(8,:,:)|Prow(9,:,:));...
  Prow(8,:,:)&(Prow(7,:,:)|Prow(9,:,:));...
  Prow(9,:,:)&(Prow(7,:,:)|Prow(8,:,:))];
hlbr=sum(hlbr,2).*pbr;

lbr=find(hlbr);
for n=1:length(lbr)
  x=fix((lbr(n)-1)/9)+1;  % the number to remove
  r=rem(lbr(n)-1,9)+1;    % the the row tow keep
  c=find(Prow(r,:,x));   % the column in Prow
%  q=fix((r-1)/3)*3+find(Prow(r,:,x)); % the quadrant
  t=zeros(3); t(rem(r-1,3)+1,:)=1;
  P(r-rem(r-1,3):r-rem(r-1,3)+2,(c-1)*3+1:(c-1)*3+3,x)=...
    P(r-rem(r-1,3):r-rem(r-1,3)+2,(c-1)*3+1:(c-1)*3+3,x)&t;
end

% if a number is in two rows or columns and two quads, it can't be in those
% rows or columns in the 3rd quad.. this may be a repetative rule

% consider when you have a total # of remaining variables & remaining spots
% spread through multiple rows / col / boxes, if you can determine which
% variable must go in a certain spot
