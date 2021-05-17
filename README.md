# test-app

FastApi based service doing async calls in slightly different favor.

## build & run
``make up``

## tear down
``make down``

## endpoints
```
http://0.0.0.0:8000/api/all?timeout=300
http://0.0.0.0:8000/api/first?timeout=300
http://0.0.0.0:8000/api/within-timeout?timeout=300
http://0.0.0.0:8000/api/smart?timeout=600
```