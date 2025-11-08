#reset docker
docker stop $(docker ps -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -q)
docker volume rm $(docker volume ls -q)

# check users table in PostgreSQL docker container
docker exec -it docker_db_1 psql -U ubuntu -d nba_db
SELECT * FROM users;

# check predictions table
SELECT id, prediction, user_verification FROM predictions;

# check logging table
# SELECT * FROM logging;

# to demo alerts being activated
docker container stop docker_api_1

docker container start docker_api_1
