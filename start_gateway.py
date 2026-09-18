import uvicorn

if __name__ == "__main__":
    uvicorn.run("strata_gateway.main:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=["services/gateway", "packages/core"])
