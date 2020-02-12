set -ex

USERNAME=ahal
IMAGE=adr
VERSION=`cat VERSION`
echo "version: $VERSION"

./build.sh
docker tag $USERNAME/$IMAGE:latest  $USERNAME/$IMAGE:$VERSION
docker push $USERNAME/$IMAGE:latest
docker push $USERNAME/$IMAGE:$VERSION
