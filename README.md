# Observer Backend

## Setting up the MySQL Database

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