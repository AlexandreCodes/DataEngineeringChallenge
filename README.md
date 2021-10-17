# Trips by week ETL - Jobsity Data Engineering Challenge
This software purpose is to extract information from predefined csv files containing data from various trips across some regions. It delivers a week average of trips by a specified criteria of the user. It also uses a scalable python rest api to process data and deliver results into a SQLite database. This software is able to scale out with a simple parameter on the docker compose command line.

## Prerequisites
- Windows 10/11 with WSDL (hasn't been tested on Linux distros)
- Docker
- Docker Compose
- Python

## Run
Execute run_program.bat or
```
docker-compose up -d --scale webetlapp=5
```
If you want to change the scale factor, just change the number after webetlapp on the command above.

## Folder Structure
```
docker-webetlapp
│   README.md
│   app.py   
│   requirements.txt
│   dockerfile
│   docker-compose.yml 
│   nginx.conf
│   run_program.bat
└─── files
│   │   trips.csv
└───database
    │   trips.db
```

## Instructions

The csv files to be processed must be placed on the "files" directory. To process files there are two endpoins that can be used. One is to specify a region and the other to specify a box of coordinates to filter the results. This docker app uses a load balancer which listens requests on localhost:4000 host and port.

The available endpoints are
```
http://localhost:4000/coordinates/<origindest>/<upper_v_lat>/<lower_v_lat>/<upper_v_lon>/<lower_v_lon>/<file_name>
http://localhost:4000/region/<region>/<file_name>
```
For the coordinates one, you must specify the parameters as such:
- <origindest> = "origin" or "dest". Lower and upper limits applied to origin or destination lat and lon coordinates
- <upper_v_lat> = Upper limit for latitude EX: 14.858954546
- <lowerr_v_lat> = Lower limit for latitude EX: 5.8987646845
- <upper_v_lon> = Upper limit for longitude EX: 14.858954546
- <lower_v_lon> = Lower limit for longitude EX: 5.8987646845
- <file_name> = Exact file name on the "files folder" without .csv suffix. EX: trips.csv -> trips

For region, you must specify the parameters as such:
- <region> = Exact name of the region. Ex: Prague
- <file_name> = Exact file name on the "files folder" without .csv suffix. EX: trips.csv -> trips

Sample Requests:
```
http://localhost:4000/region/Prague/trips
http://localhost:4000/coordinates/origin/55.98756/4.5487457/60.6547854/5.654784589/trips
```

## Output

To check the output, connect to the SQLite database. The tables are:
```
weekly_trips_by_coordinates
weekly_trips_by_region
```

The software currently is idempotent. Meaning that for a given input you will have the same output every time. The purpose of that is that you can check results for a given input without the interference of previous ones. To check the data inside database i recommend https://sqlitebrowser.org/ as a first choice for it's simplicity. Just open the file "trips.db" inside the database folder to check results.

## License
Copyright (c) 2021 Alexandre França de Magalhães

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
