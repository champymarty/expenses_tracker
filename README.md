# Expense tracker

This app track all expenses accross multiepl credit card.
It allow to combine multiple categories accros cards to accurately track the expenses

This app is meant to bu use by 1 user at a time in a local network

## Supported extractors

| Type         |            excel             |                 HTML | Language |
| ------------ | :--------------------------: | -------------------: | -------- |
| BNC          |     Yes with card number     |                   No | Eng      |
| ROGER        | Yes but categories are wrong | Yes with card number | Eng      |
| TRIANGLE     |     Yes, no card number      |                   No | Eng      |
| WEALTHSIMPLE |              No              |                   No | Eng      |

With card number means that the extractor can determine which card is used as the card number appears in.

## Run project on server

1. Create .env file
   1. Add var for UI_URLS. This is the url that are allowed on CORS for backend. Exemple: UI_URLS=http://localhost:8095,http://192.168.18.11:8095,http://172.22.240.1:8095
2. Create the initial data required at `expenses-tracker-backend/init_data.txt`

   1. One the first line write the name of the users seperated with ;
   2. On the next lines write the Sources as source_name;type;last 4 digit
   3. Exemple
      ```
      Bob;Luna;Robert
      BNC Luna card;BNC;1111
      BNC rob card;BNC;2222
      Wealthsimple Robert;WEALTHSIMPLE;3333
      ```

3. Start the project: `docker compose -f docker-compose.prod.yml up`
   if you get and error with buildkit use `DOCKER_BUILDKIT=1 docker compose -f docker-compose.prod.yml up`

## Restore db on startup

1. Create the file `espenses-tracker-backend/init_db.sql` with the script to run.
2. Input that file in the backend. There is 2 way to do it
   - Place that file in the docker volume where the expenses-tracker-backend directory is located.
   - Build the docker image with that file in the `espenses-tracker-backend/init_db.sql`. It will be copy to the docker image
3. Start/re-start the backend
