from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import subprocess
import os

app = FastAPI()

@app.post("/build")
async def build_agent(request: Request):
    data = await request.json()
    ip = data.get("ip")
    token = data.get("token")
    
    # On lit le template C++ 😌
    with open("agent_template.cpp", "r") as f:
        cpp_code = f.read()
        
    # On remplace les valeurs dynamiquement ✨
    cpp_code = cpp_code.replace("SERVER_IP_PLACEHOLDER", ip)
    cpp_code = cpp_code.replace("TOKEN_PLACEHOLDER", token)
    
    with open("agent.cpp", "w") as f:
        f.write(cpp_code)
        
    # Compilation 🥵
    subprocess.run(["x86_64-w64-mingw32-g++", "agent.cpp", "-o", "AnkyloAgent.exe", "-lwinhttp", "-mwindows", "-static"], check=False)
    
    file_path = "AnkyloAgent.exe"
    if not os.path.exists(file_path):
        with open("fallback.exe", "w") as f:
            f.write("Erreur de compilation 😱")
        file_path = "fallback.exe"
        
    return FileResponse(file_path, media_type="application/x-msdownload", filename="AnkyloAgent.exe")