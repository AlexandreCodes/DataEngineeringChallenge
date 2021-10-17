cd /d %~dp0
docker-compose up -d --scale webetlapp=5
pause