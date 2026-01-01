from robyn import SubRouter, Request, Response

statistics_router = SubRouter(__name__, prefix="/statistics")

@statistics_router.get("/:stat_id")
async def get_statistics_result(request: Request):
    """GET /statistics/{stat_id} - 获取统计分析结果"""
    pass
