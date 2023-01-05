# MESSAGING-DEMO

Demonstration of a simple sorting system composed of 3 microservices: *"scanner"*, *"compute"* and *"sorter"*. Services utilize a RabbitMQ instance to communicate with each other.

#
## How to run

The entire system can be easily deployed locally with docker-compose. From the root directory simply execute:
```
$ docker-compose up
```

### Input/Output
With the default docker-compose.yml file, volumes are mounted in a way that:
* Scanner service scans for new image files in ```data/input```
* Sorter service ouputs sorted image files in ```data/output```

New images files can be dropped to *./data/input*, scanner service will pick them up and send for processing.

Input/output directories (as well as other aspects of each service) can be configured via environment variables in the docker-compose.yml file

### Logging
Services log both to *sys.out* and to individual *log files* (configurable). By default, logging information can be observed in
```.logs``` directory.

#
## Web GUI
The system can be accessed via a simple Flask/templates web graphical interface.

With the default docker-compose.yml, web UI can be accessed at ```http://localhost:8080```.

![image](https://user-images.githubusercontent.com/10963153/184909818-eda53c2c-647b-42d9-92f3-0512099edd49.png)
