from fastapi import FastAPI

from routers.imports import router as imports_router


app = FastAPI(title="DataFlow API")

app.include_router(imports_router)


@app.get("/")
def read_root():
    return {"message": "DataFlow API is running"}