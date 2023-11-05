# Short intro
Pretty simple scraper and changer of information about MCIN authors
for mine practice at university.
It changes names of authors from form of
Smith Jhon Jhonovich(that is, full name, surname and patronymic in any order)
and make it Smith J. J.
## For startup

1. Install poetry
2. Make poetry project(`poetry new`)
3. Clone this repo(`git clone`)
4. Install dependencies(`poetry install`)
5. Run project with poetry(`poetry run python main.py`)

Classes and methods are documented,
so just read it, so you will understand most logic.

## Short explanation

There are two services in this project:
scraper and changer, scraper has two methods: scrapes information and writes it to the output file, or scrapes information and returns it as an array.
The changer has two modes (they are stored as enum):
one mode simply writes the received name changes to a file, the other mode makes the changes directly on the MCIN page.

## Flow

1. Scrape information onto a given symbol and save it to a file.
2. Initialize the changer with the changes_in_json mode to first check whether it will change names correctly.
3. If you see that some author has been incorrectly changed and you don’t know how to fix it, then add his link to blocklist.json
4. Initialize the changer with direct_changes so that the changer automatically starts replacing names. 





### Always check changed information to not heck up! Don't do *direct_changes* mode permanently, always do *changes_in_json* firstly to NOT HECK UP!