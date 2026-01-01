from robyn import SubRouter, Request, Response

qa_router = SubRouter(__name__, prefix="/qa")

@qa_router.post("/sessions")
async def create_session(request: Request):
    """POST /qa/sessions - 创建会话"""
    pass

@qa_router.post("/sessions/:session_id/messages")
async def send_message(request: Request):
    """POST /qa/sessions/{session_id}/messages - 发送问题"""
    pass

@qa_router.get("/sessions/:session_id")
async def get_session_history(request: Request):
    """GET /qa/sessions/{session_id} - 获取会话历史"""
    pass

@qa_router.delete("/sessions/:session_id")
async def delete_session(request: Request):
    """DELETE /qa/sessions/{session_id} - 删除会话"""
    pass
