from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import subprocess
import os

app = FastAPI()

@app.post("/build")
async def build_agent(request: Request):
    data = await request.json()
    ip = data.get("ip", "127.0.0.1")
    token = data.get("token", "default")
    
    # Template C++ avec WinHTTP 🥵
    agent_code = f"""#include <windows.h>
#include <winhttp.h>
#include <string>

#pragma comment(lib, "winhttp.lib")

void send_log(int event_id, const std::string& source, const std::string& message) {{
    std::string server_ip = "{ip}";
    std::string token = "{token}";
    std::string json_data = "{{\\"token\\":\\"" + token + "\\",\\"event_id\\":" + std::to_string(event_id) + ",\\"source\\":\\"" + source + "\\",\\"message\\":\\"" + message + "\\"}}";

    HINTERNET hSession = WinHttpOpen(L"AnkyloAgent/1.0", WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, 0);
    if (hSession) {{
        std::wstring wip(server_ip.begin(), server_ip.end());
        HINTERNET hConnect = WinHttpConnect(hSession, wip.c_str(), 8001, 0);
        if (hConnect) {{
            HINTERNET hRequest = WinHttpOpenRequest(hConnect, L"POST", L"/logs/ingest", NULL, WINHTTP_NO_REFERER, WINHTTP_DEFAULT_ACCEPT_TYPES, 0);
            if (hRequest) {{
                std::wstring headers = L"Content-Type: application/json\\r\\n";
                WinHttpSendRequest(hRequest, headers.c_str(), -1, (LPVOID)json_data.c_str(), json_data.length(), json_data.length(), 0);
                WinHttpReceiveResponse(hRequest, NULL);
                WinHttpCloseHandle(hRequest);
            }}
            WinHttpCloseHandle(hConnect);
        }}
        WinHttpCloseHandle(hSession);
    }}
}}

// WinMain au lieu de main() cache la console au lancement 🤫
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {{
    send_log(1, "Agent-CPP", "Agent C++ démarré avec succès ! 👍");
    return 0;
}}
"""
    
    with open("agent.cpp", "w") as f:
        f.write(agent_code)
        
    # Compilation MinGW statique et invisible ✨
    subprocess.run(["x86_64-w64-mingw32-g++", "agent.cpp", "-o", "AnkyloAgent.exe", "-lwinhttp", "-mwindows", "-static"], check=False)
    
    file_path = "AnkyloAgent.exe"
    if not os.path.exists(file_path):
        with open("fallback.exe", "w") as f:
            f.write("Erreur de compilation 😱")
        file_path = "fallback.exe"
        
    return FileResponse(file_path, media_type="application/x-msdownload", filename="AnkyloAgent.exe")