% Load and plot image white
image = imread("E:\CODE\Calib\Raw\Light_Right_11.png"); 
% Should be height\20 cm\60_white_croped_img.png
% 
% Ve theo intensity
I= rgb2gray(image);
[y,x,z] = size(image);
X=1:x;  
Y=1:y;

[xx,yy]=meshgrid(X,Y);
%i=im2d1ouble(I);
figure;mesh(yy,xx,I);
%xlim([0 y])
%zlim([190 240])
colorbar
%caxis([200 230])
%ylim([0 x])
% ve theo kenh L,a,b
% I = rgb2lab(image);
% [x,y,z] = size(I(:,:,1)); 
% X=1:x;
% Y=1:y;
% [xx,yy]=meshgrid(Y,X);
% i=im2double(I);
% figure(1);mesh(xx,yy,I(:,:,1));
% zlim([75 95])
% colorbar
% 
% I = load("D:\Paper_Nemo\Road to paper\Create_High resolution image\DE Cá 3.txt");
% [x,y,z] = size(I);
% X=1:x;
% Y=1:y;
% [xx,yy]=meshgrid(Y,X);
% i=im2double(I);
% figure(1);mesh(yy,xx,I);
% zlim([0 10])
% colorbar
% caxis([1 8])
% figure(2)
% %contour(yy,xx,I)
% contour(yy,xx,I,'ShowText','on')
% colorbar
% caxis([1 8])

