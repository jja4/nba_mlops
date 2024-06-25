#reset docker
docker stop $(docker ps -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -q)
docker volume rm $(docker volume ls -q)

#check users table in PostgreSQL docker container
docker exec -it nba_mlops_db_1 psql -U ubuntu -d nba_db
SELECT * FROM users;
# SELECT * FROM predictions;
# SELECT * FROM logging;
