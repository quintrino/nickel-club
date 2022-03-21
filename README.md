# Nickel Club
## What is the Nickel Club?
The Nickel Club is a group of Nick Wolf’s friends who can earn, spend and wager *Nickels*.

*Nickels* are a fictional currency you can earn from Nick Wolf that you can then spend for Nick to buy you fabulous prizes.

## Why does this exist?
This is a way for Nick to reward his friends when they help him grow.

## Development

### First time setup

1. Install postgres and create a database
2. Create a `.env` file in the project root containing the following

```sh
DATABASE_URL='<DATABASE URL GOES HERE>'
SECRET_KEY=dev
FLASK_ENV=development
```
3. `poetry install`
4. `poetry shell`
5. `flask init-db` (this creates the tables)
6. `flask run`

### Once you're already set up
1. `poetry shell`
2. `flask run`
