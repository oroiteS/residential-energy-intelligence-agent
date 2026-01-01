from robyn import SubRouter, Request, Response

reports_router = SubRouter(__name__, prefix="/reports")

@reports_router.get("/:report_id")
async def get_report_status(request: Request):
    """GET /reports/{report_id} - 查询报告状态"""
    pass

@reports_router.get("/:report_id/download")
async def download_report(request: Request):
    """GET /reports/{report_id}/download - 下载报告"""
    pass
