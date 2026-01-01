from robyn import SubRouter, Request, Response

jobs_router = SubRouter(__name__, prefix="/jobs")

@jobs_router.get("/:job_id")
async def get_job_status(request: Request):
    """GET /jobs/{job_id} - 获取任务状态"""
    pass

@jobs_router.post("/:job_id/cancel")
async def cancel_job(request: Request):
    """POST /jobs/{job_id}/cancel - 取消任务"""
    pass
