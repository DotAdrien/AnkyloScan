#include <windows.h>
#include <winhttp.h>
#include <string>
#include <vector>
#include <algorithm>

#pragma comment(lib, "winhttp.lib")

void send_log(int event_id, const std::string& source, const std::string& message) {
    std::string server_ip = "SERVER_IP_PLACEHOLDER";
    std::string token = "TOKEN_PLACEHOLDER";
    // Échappement basique pour le JSON au cas où
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
    send_log(1, "Agent-AD", "Démarré en arrière-plan ! ✨");
    
    // Historique des logs déjà envoyés pour éviter les doublons 🧠
    std::vector<std::string> seen_logs;

    while (true) {
        // On cherche sur les 15 dernières secondes (chevauchement avec la pause de 10s pour être sûr de rien rater)
        FILE* pipe = _popen("powershell -WindowStyle Hidden -command \"Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625; StartTime=(Get-Date).AddSeconds(-15)} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty TimeCreated\"", "r");
        
        if (pipe) {
            char buffer[256];
            while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
                std::string line = buffer;
                
                // On nettoie la ligne (enlève les espaces et retours à la ligne) 🧹
                line.erase(line.find_last_not_of(" \n\r\t") + 1);
                
                if (line.length() > 5) {
                    // Si la date n'est PAS dans notre historique, on l'envoie ! 🚀
                    if (std::find(seen_logs.begin(), seen_logs.end(), line) == seen_logs.end()) {
                        
                        send_log(4625, "Agent-AD", "Échec de mot de passe à " + line + " 😱");
                        
                        // On l'ajoute à la mémoire
                        seen_logs.push_back(line);
                        
                        // On limite la mémoire à 50 éléments pour ne pas saturer la RAM 🧠
                        if (seen_logs.size() > 50) {
                            seen_logs.erase(seen_logs.begin());
                        }
                    }
                }
            }
            _pclose(pipe);
        }
        Sleep(10000); // Pause 😪
    }
    return 0;
}