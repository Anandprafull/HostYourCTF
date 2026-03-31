Command 1 - Stop Docker completely:
docker-compose down -v --remove-orphans

Command 2 - Force remove all volumes:
docker volume rm ctfd_db_data

Command 3 - List remaining volumes to verify:
docker volume ls

(This should show EMPTY or no ctfd volumes)

Command 4 - Remove all unused Docker stuff:
docker system prune -a -f --volumes

Command 5 - Start fresh:
docker-compose up -d

Command 6 - Wait 25 seconds:
timeout /t 25

Command 7 - Verify empty database:
docker-compose exec db mysql -u root -pctfd ctfd -e "SHOW TABLES;"

(Should show 0 or error - meaning fresh database)

Command 8 - Import fresh questions:
python import_challenges_v3.py

Command 9 - Check admin panel:
http://localhost/admin/challenges

