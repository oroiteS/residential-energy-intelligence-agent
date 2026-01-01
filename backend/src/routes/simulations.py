from robyn import SubRouter, Request, Response

simulations_router = SubRouter(__name__, prefix="/simulations")

@simulations_router.post("/")
async def create_simulation(request: Request):
    """POST /simulations - 创建模拟任务"""
    pass

@simulations_router.post("/:simulation_id/trigger")
async def trigger_simulation(request: Request):
    """POST /simulations/{simulation_id}/trigger - 手动触发生成"""
    pass

@simulations_router.get("/:simulation_id")
async def get_simulation_status(request: Request):
    """GET /simulations/{simulation_id} - 获取任务状态"""
    pass

@simulations_router.delete("/:simulation_id")
async def delete_simulation(request: Request):
    """DELETE /simulations/{simulation_id} - 删除模拟任务"""
    pass
