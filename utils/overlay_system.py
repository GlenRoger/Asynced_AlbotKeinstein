#Skal funke, men hva er feil... :(

import asyncio
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

class OverlaySystem:
    def __init__(self, logger, host="127.0.0.1", port=8000):

        pass

        # self.logger_prefix = "utils/OverlaySystem=>"
        # self.logger = logger
        # self.host = host
        # self.port = port
        # self.app = FastAPI()
        # self.server_task = None
        # self.current_text = "Green Screen Overlay Working!"
        
        # # Create directory for static files if it doesn't exist
        # os.makedirs("overlay_static", exist_ok=True)
        
        # # Set up templates folder
        # os.makedirs("overlay_templates", exist_ok=True)
        # self.templates = Jinja2Templates(directory="overlay_templates")
        
        # # Create template files if they don't exist
        # self.create_default_files()
        
        # self.setup_routes()
    
    def create_default_files(self, show_text):
        """Create default template and CSS files for the overlay"""
        template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream Overlay</title>
    <link rel="stylesheet" href="/static/style.css">
    <meta http-equiv="refresh" content="1">
</head>
<body>
    <div class="overlay-container">
        <div id="green-screen"></div>
        <div id="display-text">{{ text }}</div>
    </div>
</body>
</html>
"""
        
        css_content = """body {
    margin: 0;
    padding: 0;
    overflow: hidden;
}

.overlay-container {
    width: 100vw;
    height: 100vh;
    position: relative;
}

#green-screen {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: #00FF00;  /* Green screen color */
    z-index: -1;
}

#display-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 2em;
    color: white;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}
"""
        
        with open("overlay_templates/index.html", "w") as f:
            f.write(template_content)
            
        with open("overlay_static/style.css", "w") as f:
            f.write(css_content)
            
        self.logger.info(f"{self.logger_prefix}Created basic green screen overlay files")
    
    def setup_routes(self):
        """Setup the routes for the FastAPI application"""
        # Mount static files directory
        self.app.mount("/static", StaticFiles(directory="overlay_static"), name="static")
        
        @self.app.get("/", response_class=HTMLResponse)
        async def get_overlay(request: Request):
            """Serve the main overlay HTML page with current text"""
            self.logger.info(f"{self.logger_prefix}Serving overlay with text: {self.current_text}")
            return self.templates.TemplateResponse(
                "index.html", 
                {"request": request, "text": self.current_text}
            )
    
    async def update_text(self, new_text):
        pass

        """Update the text displayed on the overlay"""
        # current_log_prefix = self.logger_prefix + "update_text:"

        # self.logger.info(f"{current_log_prefix}Updating overlay text to: {new_text}")

        # self.current_text = new_text

    
    async def start_server(self):
        """Start the FastAPI server"""
        self.logger.info(f"{self.logger_prefix}Starting simple green screen overlay server on {self.host}:{self.port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="error"
        )
        
        server = uvicorn.Server(config)
        self.server_task = asyncio.create_task(server.serve())
        return self.server_task
    
    async def stop_server(self):
        """Stop the FastAPI server"""
        self.logger.info(f"{self.logger_prefix}Stopping overlay server")
        
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass