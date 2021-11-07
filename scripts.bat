@REM I ran the commands below one at a time in the project environment
docker build --tag docker-msg .
docker tag docker-msg:latest docker-msg:v1.0.0

@REM Change the statements below to reference your docker ID.
docker tag docker-msg:latest docker.io/keyuyan1145/docker-msg

docker run -p 5000:5000 keyuyan1145/docker-msg
@REM docker push docker.io/keyuyan1145/docker-msg

@REM I ran the commands below on the EC2 console
@REM docker pull docker.io/keyuyan1145/docker-msg
@REM docker run -p 5000:5000 docker.io/keyuyan1145/docker-msg