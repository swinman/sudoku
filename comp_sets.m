function [P]=comp_sets(P)
% takes in and updates probability array
% using complete sets to eliminate possibilities outside of the set
% eliminate options outside of a complete set - 1,9 in 2 boxes means they
% can't be anywhere else... if a set of n boxes only contains n variables,
% those variables can't be anywhere else in the row / column / box
% only possible when the number of boxes with <= n options >= n
% (# of boxes w/ > 2 options)*(areas with 2 or more w/ 2 options)
% so: length(unique([find(P(i,j,:)_1) find(P(i,j,:)_2) find(P(i,j,:)_n)]))
% only potentially helpful when number of unknowns in the row/col/box > n
% check if any group of sum(sum(P,3)~=1)-1 is unique

num_pot=sum(P,3); runk=sum(num_pot~=1,2);
for r=1:9   % test all rows
  for t=2:(runk(r)-1)   % t is the size of the set to test for
    c=find(num_pot(r,:)>1&num_pot(r,:)<=t); % location of places to check
    if  length(c)>=t        % if there are enough possible locations
 %   fprintf('\nRow: %0.0f, Test Size: %0.0f\nLocations: ',r,t)
 %   disp(c)
      C = nchoosek(c,t); % matrix of all t size combos of objects in c
      for n=1:size(C,1);
        vs=zeros(1,t^2+1);    % vect with all potential values for a set
        for a=1:t, x=find(P(r,C(n,a),:));  vs(a*t-length(x)+1:a*t)=x;  end
        if length(unique(vs))<=t-1
          x=unique(vs); x=x(2:end); c=C(n,:); i=r;
          pr=sum(sum(P(i,:,x)))-length(c)*length(x);
          if pr>0, %fprintf('%0.0f potentials removed\n',pr)
%          disp('GOT ONE'), disp(unique(vs)), disp(C(n,:)), disp(r)
          A=ones(9,9,9); A(r,:,x)=0; A(r,c,x)=1; P=P&A;
          end
        end
      end
    end
  end
end

num_pot=sum(P,3); cunk=sum(num_pot~=1); 
for c=1:9   % test all columns
  for t=2:(cunk(c)-1)   % t is the size of the set to test for
    r=find(num_pot(:,c)>1&num_pot(:,c)<=t);    % location of places to check
    if  length(r)>=t        % if there are enough possible locations
%    fprintf('Col: %0.0f, Test Size: %0.0f\nLocations:\n',c,t)
      R = nchoosek(r,t);  % matrix of all t size combos of objects in r
      for n=1:size(R,1);
        vs=zeros(1,t^2+1);  % vect with all potential values for a set
        for a=1:t, x=find(P(R(n,a),c,:));  vs(a*t-length(x)+1:a*t)=x;  end
        if length(unique(vs))<=t-1   % if you have a complete set
          x=unique(vs); x=x(2:end); r=R(n,:); j=c;
          pr=sum(sum(P(:,j,x)))-length(r)*length(x);
          if pr>0, %fprintf('%0.0f potentials removed\n',pr)
 %         disp('GOT ONE'), disp(unique(vs)), disp(R(n,:)), disp(c)
          A=ones(9,9,9); A(:,c,x)=0; A(r,c,x)=1; P=P&A;
          end
        end
      end
    end
  end
end

num_pot=sum(P,3); bunk=zeros(1,9);
for q=1:9,
  i=fix((q-1)/3)*3+1; j=rem(q-1,3)*3+1;
  bunk(q)=sum(sum(num_pot(i:i+2,j:j+2)~=1));
end

for q=1:9   % test all quadrants
  for t=2:(bunk(q)-1)   % t is the size of the set to test for
    cs=rem(q-1,3)*3+1; rs=fix((q-1)/3)*3+1;
    pl=find(num_pot(rs:rs+2,cs:cs+2)>1&num_pot(rs:rs+2,cs:cs+2)<=t);
    if  length(pl)>=t        % if there are enough possible locations
      PL = nchoosek(pl,t);  R=rem(PL-1,3)+rs; C=fix((PL-1)/3)+cs;
      for n=1:size(R,1);
        vs=zeros(1,t^2+1);  % vect with all potential values for a set
        for a=1:t, x=find(P(R(n,a),C(n,a),:));...
            vs(a*t-length(x)+1:a*t)=x;  end
        if length(unique(vs))<=t-1   % if you have a complete set
          x=unique(vs); x=x(2:end); r=R(n,:); c=C(n,:);
%          disp('GOT ONE'), disp(unique(vs)), disp(R(n,:)), disp(c), disp(q)
%          disp(cs), disp(rs)
          pr=sum(sum(sum(P(rs:rs+2,cs:cs+2,x))))-length(r)*length(x);
          if pr>0, %fprintf('%0.0f potentials removed\n',pr)
            A=ones(9,9,9); A(rs:rs+2,cs:cs+2,x)=0; 
            for ji=1:length(r), A(r(ji),c(ji),x)=1; end
            P=P&A;
          end
        end
      end
    end
  end
end

