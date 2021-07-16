NAME=
VERSION=
ACR=

sudo docker build -t $ACR.azurecr.io/$NAME:$VERSION -f Dockerfile .
sudo docker push $ACR.azurecr.io/$NAME:$VERSION