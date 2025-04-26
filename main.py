from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI on Vercel!"}

@app.get("/test/{id}")
async def test(id: int):
    return {"id": id, "message": "Test endpoint"}