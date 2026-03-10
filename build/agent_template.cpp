#include <windows.h>
#include <winhttp.h>
#include <string>

#pragma comment(lib, "winhttp.lib")

void send_log(int event_id, const std::string& source, const std::string& message) {
    std::string server_ip = "SERVER_IP_PLACEHOLDER";
    std::string token = "TOKEN_PLACEHOLDER";
    std::string json_data = "{\"token\":\"" + token + "\",\"event_id\":" + std::to_string(event_id) + ",\"source\":\"" + source + "\",\"message\":\"" + message + "\"}";

    HINTERNET hSession = WinHttpOpen(L"AnkyloAgent/1.0", WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, 0);
    if (hSession) {
        std::wstring wip(server_ip.begin(), server_ip.end());
        HINTERNET hConnect = WinHttpConnect(hSession, wip.c_str(), 8001, 0);
        if (hConnect) {
            HINTERNET hRequest = WinHttpOpenRequest(hConnect, L"POST", L"/logs/ingest", NULL, WINHTTP_NO_REFERER, WINHTTP_DEFAULT_ACCEPT_TYPES, 0);
            if (hRequest) {
                std::wstring headers = L"Content-Type: application/json\r\n";
                WinHttpSendRequest(hRequest, headers.c_str(), -1, (LPVOID)json_data.c_str(), json_data.length(), json_data.length(), 0);
                WinHttpReceiveResponse(hRequest, NULL);
                WinHttpCloseHandle(hRequest);
            }
            WinHttpCloseHandle(hConnect);
        }
        WinHttpCloseHandle(hSession);
    }
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    send_log(1, "Agent-CPP", "Agent démarré avec succès ! 👍");
    return 0;
}