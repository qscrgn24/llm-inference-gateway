from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI(
        title="LLM Inference Gateway",
        version="1.0.0",
    )

    @app.get("/v1/health")
    def health():
        return {
            "status" : "ok",
            "version" : app.version,
        }
    
    return app

app = create_app