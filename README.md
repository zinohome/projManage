# Swiftapp

## Develop

uvicorn main:app --host '0.0.0.0' --port 8000 --reload

uvicorn backend/main:app --host '0.0.0.0' --port 8000 --reload


hypercorn -c appconfig/hypercorn-dev.py -w 1 --reload main:app


