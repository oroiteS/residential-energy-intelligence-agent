from robyn import SubRouter, Request, Response

anomalies_router = SubRouter(__name__, prefix="/anomalies")

@anomalies_router.get("/:anomaly_id")
async def get_anomaly_result(request: Request):
    """GET /anomalies/{anomaly_id} - 获取异常检测结果"""
    pass
