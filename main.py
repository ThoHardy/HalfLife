import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Request, Form, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from crud import TaskManagerCRUD

app = FastAPI()

# -- Configuration --
APP_PASSWORD = os.environ.get("APP_PASSWORD", "minuit329")
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
DATABASE_ID = os.environ.get("DATABASE_ID", "minuit-database")

# Initialize Task Manager
try:
    tm = TaskManagerCRUD(project_id=PROJECT_ID, database_id=DATABASE_ID)
except Exception as e:
    print(f"Warning: Firestore client init failed: {e}")
    tm = None

templates = Jinja2Templates(directory="templates")

# -- Auth Dependency --
def get_current_user(auth_token: Optional[str] = Cookie(None)):
    if auth_token != APP_PASSWORD:
        return None
    return auth_token

# -- Routes --

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, user: Optional[str] = Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    tasks = []
    stats = []
    
    if tm:
        tasks = tm.get_all_tasks()
        stats = tm.get_7_day_stats()

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "tasks": tasks, 
        "stats": stats
    })
    
@app.post("/login")
async def login(password: str = Form(...)):
    if password == APP_PASSWORD:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="auth_token", value=password, httponly=True)
        return response
    return HTMLResponse(content="Invalid Password", status_code=401)

@app.post("/tasks")
async def add_task(
    name: str = Form(...),
    half_life: float = Form(...),
    difficulty: int = Form(1),
    is_recurrent: bool = Form(False),
    user: Optional[str] = Depends(get_current_user)
):
    if not user: raise HTTPException(status_code=401)
    if tm:
        tm.add_task(name, half_life, difficulty, is_recurrent)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/tasks/{task_id}/update")
async def update_task(
    task_id: str,
    name: str = Form(...),
    half_life: float = Form(...),
    difficulty: int = Form(1),
    user: Optional[str] = Depends(get_current_user)
):
    if not user: raise HTTPException(status_code=401)
    if tm:
        tm.update_task(task_id, name, half_life, difficulty)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/tasks/{task_id}/done")
async def complete_task(task_id: str, user: Optional[str] = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    if tm:
        tm.complete_task(task_id)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/tasks/{task_id}/delete")
async def delete_task(task_id: str, user: Optional[str] = Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    if tm:
        tm.delete_task(task_id)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))