import pathlib
import os

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from starlette.routing import Route

app = FastAPI()

# Turn off CORS (allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_frontend_router(build_dir="frontend/dist"):
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir

    if not os.path.isdir(build_path) or not (build_path / "index.html").is_file():
        print("Warning: Frontend build directory not found or index.html missing.")
        # Return a dummy router if build isn't ready

        async def dummy_frontend():
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )
        return Route("/{path:path}", endpoint=dummy_frontend)
    
    return StaticFiles(directory=build_path, html=True)

app.mount("/app",
          create_frontend_router(),
          name="frontend"
)
