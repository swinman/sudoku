function OK=check_ok(P)
% checks if a solution is possible, retuns 1 for yes 0 for no

OK = 1;
num_pot=sum(P,3);
row_pot=permute(sum(P,2),[3 1 2]);  %(x,r)=potential locations for x in row
col_pot=permute(sum(P),[3 2 1]);    %(x,c)=potential locations for x in col
box_pot=col_pot*0;
for x=1:9
  for q=1:9
    i=fix((q-1)/3)*3+1; j=rem(q-1,3)*3+1;
    box_pot(x,q)=sum(sum(P(i:i+2,j:j+2,x)));
  end
end

if find(~num_pot) ~= 0
  t = find(~num_pot);   OK = 0;
  for n=1:length(t)
    r = rem((t(n)-1),9)+1; c = fix((t(n)-1)/9)+1;
    fprintf('No number works in row %0.0f col %0.0f\n',r,c)
  end
end

if find(~row_pot) ~= 0
  t = find(~row_pot);   OK = 0;
  for n=1:length(t)
    x = rem((t(n)-1),9)+1; r = fix((t(n)-1)/9)+1;
    fprintf('%0.0f cant go in row %0.0f\n',x,r)
  end
end

if find(~col_pot) ~= 0
  t = find(~col_pot);   OK = 0;
  for n=1:length(t)
    x = rem((t(n)-1),9)+1; c = fix((t(n)-1)/9)+1;
    fprintf('%0.0f cant go in col %0.0f\n',x,c)
  end
end

if find(~box_pot) ~= 0
  t = find(~box_pot);   OK = 0;
  for n=1:length(t)
    x = rem((t(n)-1),9)+1; q = fix((t(n)-1)/9)+1;
    fprintf('%0.0f cant go in quad %0.0f\n',x,q)
  end
end

if OK == 1;
  disp('all OK')
end
