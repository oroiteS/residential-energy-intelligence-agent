from robyn import SubRouter, Request, Response

behavior_router = SubRouter(__name__, prefix="/behavior-analyses")

@behavior_router.get("/:analysis_id")
async def get_behavior_result(request: Request):
    """GET /behavior-analyses/{analysis_id} - 获取行为分析结果"""
    pass
