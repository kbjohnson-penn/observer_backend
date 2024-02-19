# Observer Backend

## Installation

Follow these steps to get your development environment set up:

1. Clone the repository:

```bash
git clone https://github.com/kbjohnson-penn/observer_backend.git
cd observer_backend
```

2. Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the requirements:

```bash
pip install -r requirements.txt
```

4. Install [MySQL](https://www.mysql.com/) or [MariaDB](https://mariadb.com/) database.

## Configuration

Before running the project, configure your environment variables:

Copy `.env.example` to `.env` and fill in the necessary settings.

### Setting up the MySQL Database

1. **Open MySQL command line tool or MySQL Shell**: You can do this by typing `mysql -u root -p` in your terminal and then entering your MySQL root password when prompted.

2. **Create a new database**: Once you're in the MySQL shell, you can create a new database by running the `CREATE DATABASE` command. For example, if you want to create a database named `observer_dashboard_database`, you would run `CREATE DATABASE observer_dashboard_database;`.

3. **Create a new user**: You can create a new user by running the `CREATE USER` command. For example, if you want to create a user named `observer`, you would run `CREATE USER 'observer'@'localhost' IDENTIFIED BY 'observer123';`.

4. **Grant permissions**: After creating the user, you can grant them permissions to a database using the `GRANT` command. For example, to grant all permissions to the `observer_dashboard_database` database to the `observer` user, you would run `GRANT ALL PRIVILEGES ON observer_dashboard_database.* TO 'observer'@'localhost';`.

5. **Flush privileges**: Finally, you need to run the `FLUSH PRIVILEGES;` command to reload the grant tables and put your new changes into effect.

Here's what the commands look like:

```bash
mysql -u root -p
CREATE DATABASE observer_dashboard_database;
CREATE USER 'observer'@'localhost' IDENTIFIED BY 'observer123';
GRANT ALL PRIVILEGES ON observer_dashboard_database.* TO 'observer'@'localhost';
FLUSH PRIVILEGES;
```

## Running the Project

Apply the database migrations to create the database schema

```bash
python manage.py makemigrations
python manage.py migrate
```

Create a Django admin user

```bash
python manage.py createsuperuser
```

To run the Django project locally:

```bash
python manage.py runserver
```
 
- Open [http://127.0.0.1:8000/api](http://127.0.0.1:8000/api) to view all the API routes.
- Open [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) to login and add new records to the database.

## Contributing

Please read [CONTRIBUTING](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Changelog

Check [CHANGELOG](CHANGELOG.md) to get the version details.
