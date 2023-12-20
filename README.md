# School Contact Scraper

## Description
This Python application uses Selenium, running in a Dockerized environment, to scrape school websites for contact information. It iterates over a predefined list of places, accesses a school listing website for each, collects URLs for individual schools, and scrapes each school's website for contact details like email addresses.

## Prerequisites
Before you begin, ensure you have met the following requirements:
- Docker and Docker Compose are installed on your machine.
- Basic knowledge of Docker and containerization.

## Setup
To set up the School Contact Scraper, follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the cloned directory.

## Running the Application
To run the application, execute the following command in the terminal:

```sh
docker-compose up --build
```

This command builds the Docker images and starts the containers as defined in your `docker-compose.yml` file. Specifically, it sets up a Selenium Hub, a Chrome node, and your application in separate containers.

## Files and Directories
The project structure includes the following files and directories:
- `docker-compose.yml`: Defines the multi-container Docker applications.
- `Dockerfile`: Instructions for building the application's Docker image.
- `requirements.txt`: Lists the Python dependencies for the application.
- `scrape.py`: The main Python script for scraping websites.
- `school_emails.csv`: File where scraped email addresses are stored.
- `wait-for-it.sh`: A script for controlling the order of service startup in Docker Compose.

## Stopping the Application
To stop the application and remove the containers, networks, and volumes created by `docker-compose up`, run:

```sh
docker-compose down
```

## Additional Notes
- Ensure that the ports defined in `docker-compose.yml` are available on your machine.
- The application's behavior can be modified by changing the list of places in `scrape.py`.

## Contributing
For any contributions or suggestions, please open an issue or submit a pull request.
