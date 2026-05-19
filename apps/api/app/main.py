from fastapi import FastAPI

app = FastAPI(title="Synapse API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
