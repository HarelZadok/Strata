from fastapi import FastAPI
from strata_core.logging import setup_logging

setup_logging()

app = FastAPI(title="Strata API Gateway")

@app.get("/")
def read_root():
    return {"message": "Strata API Gateway is running"}
