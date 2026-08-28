from fastapi import APIRouter, HTTPException
from models.task import Task, TaskUpdate
from database import supabase

router = APIRouter()

@router.get("/tasks")
async def get_tasks():
    try:
        response = supabase.table("tasks").select("*").execute()
        return {"tasks": response.data}

    except Exception as e:
        return {"error": str(e)}

@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    try:
        response = supabase.table("tasks").select("*").eq("id",task_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Task not found")

        return {"task": response.data}

    except HTTPException:
        raise
        
    except Exception as e:
        return {"error": str(e)}

@router.post("/tasks")
async def create_task(task: Task):
    try:
        response = supabase.table("tasks").insert({
            "title":task.title,
            "description":task.description,
        }).execute()

        return {"task": response.data}

    except Exception as e:
        return {"error": str(e)}    

@router.patch("/tasks/{task_id}")
async def update_task(task_id: str, task: TaskUpdate):
    try:
        update_data = task.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update.")

        response = supabase.table("tasks").update(update_data).eq("id", task_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"task": response.data}

    except HTTPException:
        raise

    except Exception as e:
        return {"error": str(e)}
    
@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    try:
        response = supabase.table("tasks").delete().eq("id", task_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Task not found")

        return {"message": "Task deleted successfully."}

    except HTTPException:
        raise

    except Exception as e:
        return {"error": str(e)}
    