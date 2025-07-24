from multi_step_agent import multi_step_agent
from acp_sdk.server import create_app
from fastapi.middleware.cors import CORSMiddleware

app = create_app(multi_step_agent)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
