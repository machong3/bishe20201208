clc,clear
yt=load('24.txt');%апоРа©
yt
n=length(yt);alpha=[0.2,0.5,0.8];m=length(alpha);
ywhat(1,[1:m])=(yt(1)+yt(2))/2;
for i=2:n
    ywhat(i,:)=alpha*yt(i-1)+(1-alpha).*ywhat(i-1,:);
end
ywhat
err=sqrt(mean((repmat(yt,1,m)-ywhat).^2))
%xlswrite('dianqi.xls',ywhat)
ywhat1988=alpha*yt(n)+(1-alpha).*ywhat(n,:)