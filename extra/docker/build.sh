set -ex
USERNAME=ahal
IMAGE=adr

pip-compile --generate-hashes --upgrade requirements.in
docker build -t $USERNAME/$IMAGE:latest .
