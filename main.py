from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
# import url
from api.url import router as api_url
from webhooks.webhook import webhook_router
templates = Jinja2Templates(directory="GUI/templates")
# Mount the static files directory

app = FastAPI()
app.mount("/static", StaticFiles(directory="GUI/static"), name="static")
app.include_router(api_url)
app.include_router(webhook_router)


# render template
@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
