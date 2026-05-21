# VetClínica - Sistema de Gestão Veterinária

A full-stack web application designed to manage a veterinary clinic. It allows for the management of animal patients, appointments, and medical histories. The system is built with a microservices architecture and is fully containerized using Docker for easy deployment and scalability.

## Features

-   **Authentication:** Secure login system for authorized users using JWT.
-   **Dashboard:** An overview of key clinic statistics, including the number of registered animals, total consultations, and upcoming appointments.
-   **Animal Management (CRUD):**
    -   Register new animal patients with details like species, breed, age, owner information, and observations.
    -   View a comprehensive list of all animals with search and filter capabilities.
    -   Update patient information.
    -   Remove animal records from the system.
-   **Consultation Management (CRUD):**
    -   Schedule new consultations for registered animals.
    -   Record detailed information for each appointment, including motive, diagnosis, treatment, and prescribed medications.
    -   View a complete history of all consultations, filterable by status (Scheduled, Completed, Canceled).
    -   Update or cancel existing appointments.

## Architecture

The application is designed using a microservices architecture, with each component running in its own Docker container:

-   **Frontend (`mq1-frontend`):** A client-side application built with HTML, CSS, and Vanilla JavaScript, served by an **Nginx** web server. It provides the user interface and handles all user interactions.
-   **Backend (`mq2-backend`):** A RESTful API developed with **Python** and **FastAPI**. It manages all business logic, data validation, user authentication, and communication with the database.
-   **Database (`mq3-database`):** A **PostgreSQL** database that persists all application data, including animal and consultation records. The database is initialized with a predefined schema and sample data.

All services are orchestrated by **Docker Compose**, ensuring a smooth and consistent setup process.

## Technology Stack

-   **Backend:** Python 3.11, FastAPI, SQLAlchemy, Pydantic, python-jose (JWT)
-   **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+)
-   **Database:** PostgreSQL 15
-   **Web Server:** Nginx
-   **Containerization:** Docker, Docker Compose

## Getting Started

Follow these steps to run the application locally.

### Prerequisites

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1.  Clone the repository to your local machine:
    ```sh
    git clone https://github.com/albibino/t2-clinica-veterinaria.git
    ```

2.  Navigate to the project's root directory:
    ```sh
    cd t2-clinica-veterinaria
    ```

3.  Build and run the containers in detached mode using Docker Compose:
    ```sh
    docker-compose up -d --build
    ```
    The services will start in the following order: database, backend, and then frontend. The backend includes a health check to wait for the database to be ready before starting.

4.  Access the application by navigating to `http://localhost` in your web browser.

5.  Log in using the default credentials:
    -   **Username:** `admin`
    -   **Password:** `admin123`

### Stopping the Application

To stop and remove the containers, run the following command in the project root directory:
```sh
docker-compose down