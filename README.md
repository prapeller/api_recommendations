## Search service
https://github.com/prapeller/Async_API_sprint_2

- provides films search possibility by name/genre and other film properties


## Auth service
https://github.com/prapeller/Auth_sprint_2

- provides user session control by authentication/authorization


## UGC service
https://github.com/prapeller/ugc_sprint_2

- provides possibility for users collect and control their activity
- provides possibility for analytics team analise users activity, make business conclusions, and improve online cinema based on these conclusions


## Notification service
https://github.com/prapeller/notifications_sprint_1

- provides possibility for users to receive/not receive (switch off/on) notifications (email / telegram / interface)
- provides possibility for cinema to send notifications:

## Recommendations service
https://github.com/prapeller/graduate_work

- provides possibility for users to get the recommended films based on their ugc

notes:
- weight - importance of vector
- film vector - list of dots-floats, vectorized based on genre.text (weight 3) / description.text (weight 2) / type.text (weight 1))
- mongo_ugc - mongo db from 'ugc service' with user likes (film_uuid list)
- postgres_search - postgresql db from 'search service' with films film_uuid/genre(varchar)/description(text)/type(varchar)

containers:
- vector_recommendations (milvus)
  - stores film vectors (film_uuid: [point, point]) at vector in-memory vector db
- api_recommendations
  - fastapi based http interface to 
    - get/set film vectors to vector db
    - recommend films for current user
- etl_postgres_to_vector_recommendations
  - constantly (on any postgres_search.film table update (triggered on comparison of film.updated_at field timestamp and lastly index update timestamp in 'last_etl_update' file)) extracting updated film_data, transforming with gensim(word2vec model), and loading to vector_recommendations using fastapi post route
- redis_recommendations
  - stores in redis cache recent frontend requests results

data flow:
- etl_postgres_to_vector_recommendations loads updated films vectors to vector_db
- api_recommendations (after user request) 
  - checks cache_recommendations first
  - if cache miss, it goes to mongo_api for getting list of current_user bookmarked film_uuid list, and request vector_recommendations to get a film_uuid list of similar film vectors
  - film_uuid list is stored in redis_recommendations and sent back to the frontend

# 1) Deploy locally (api at host)
- > make api-redis-build-loc
- > cd api_recommendations
  > python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements/local.txt
- > export DEBUG=True && export DOCKER=False && python main.py
- swagger docs can be found at 127.0.0.1:8085/docs


# 2) Deploy locally (api at docker container)
- > make build-loc
- swagger can be found at 127.0.0.1:85/docs