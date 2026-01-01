from robyn import SubRouter, Request, Response

dashboard_router = SubRouter(__name__, prefix="/dashboards")

@dashboard_router.get("/:dataset_id")
async def get_dashboard_data(request: Request):
    """GET /dashboards/{dataset_id} - 获取看板数据"""
    pass
