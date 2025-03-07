# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from trenex import Trenex  # Your builder class from trenex.py
from core.plugin.plugin_factory import create_template, package_plugin

app = FastAPI(title="Trenex API", version="1.0")

# Create a global builder instance.
builder = Trenex()

# ----------------------------------------------------------------
# Request models
# ----------------------------------------------------------------
class TrenexRequest(BaseModel):
    name: str

class PluginTemplateRequest(BaseModel):
    plugin_name: str
    plugin_type: str
    output_dir: str = "./plugins/"  # Default folder for plugin templates

class PluginPackageRequest(BaseModel):
    plugin_folder: str
    output_dir: str = "./plugins/packaged/"  # Default folder for packaged plugins

# ----------------------------------------------------------------
# Trenex control endpoints
# ----------------------------------------------------------------
@app.post("/trenex/start")
def start_bot(req: TrenexRequest):
    try:
        builder.start_new_trnx(req.name)
        return {"message": f"Bot '{req.name}' started."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/trenex/build")
def build_bot():
    try:
        builder.build()
        return {"message": "Bot built successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/trenex/run")
def run_bot():
    try:
        bot = builder.get_trnx()
        bot.run()
        return {"message": "TRNX is running."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ----------------------------------------------------------------
# Plugin template endpoints (using plugin factory API)
# ----------------------------------------------------------------
@app.post("/plugin/template")
def create_plugin_template(req: PluginTemplateRequest):
    try:
        # Using static methods defined in Trenex to wrap plugin factory functionality.
        template_path = create_template(
            req.plugin_name, req.plugin_type, req.output_dir
        )
        return {
            "message": f"Plugin template for '{req.plugin_name}' created.",
            "template_path": template_path,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/plugin/package")
def package_plugin_template(req: PluginPackageRequest):
    try:
        plg_path = package_plugin_template(
            req.plugin_folder, req.output_dir
        )
        return {
            "message": "Plugin packaged successfully.",
            "plg_path": plg_path,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
