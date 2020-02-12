set -ex
USERNAME=ahal
IMAGE=adr

pip-compile --generate-hashes requirements.in
docker build -t $USERNAME/$IMAGE:latest .
