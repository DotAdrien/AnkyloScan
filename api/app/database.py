from fastapi import APIRouter

router = APIRouter(prefix="/db", tags=["Database 🐬"])

@router.get("/history")
def get_scan_history():
    # Liste de scans fictifs avec les types demandés 🧪
    return [
        {
            "id": 101,
            "type": 3, # Rose (Complet)
            "time": "04/02/2026 - 21:30",
            "description": "Analyse des versions et vulnérabilités sur 192.168.1.0/24 terminée. 🛡️"
        },
        {
            "id": 102,
            "type": 2, # Bleu (Sécurité)
            "time": "04/02/2026 - 18:15",
            "description": "Détection des ports ouverts et adresses MAC effectuée. 👍"
        },
        {
            "id": 103,
            "type": 1, # Vert (Rapide)
            "time": "04/02/2026 - 09:00",
            "description": "Scan rapide du réseau local terminé avec succès. ✨"
        }
    ]