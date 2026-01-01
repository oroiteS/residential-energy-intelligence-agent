from robyn import SubRouter, Request, Response

patterns_router = SubRouter(__name__, prefix="/load-patterns")

@patterns_router.get("/:pattern_id")
async def get_pattern_result(request: Request):
    """GET /load-patterns/{pattern_id} - 获取负荷模式结果"""
    pass
