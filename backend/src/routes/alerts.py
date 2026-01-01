from robyn import SubRouter, Request, Response

alerts_router = SubRouter(__name__, prefix="/alert-config")

@alerts_router.get("/")
async def get_alert_config(request: Request):
    """GET /alert-config - 获取告警配置"""
    pass

@alerts_router.put("/")
async def update_alert_config(request: Request):
    """PUT /alert-config - 更新告警配置"""
    pass
