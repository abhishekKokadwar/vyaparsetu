import uvicorn
import os

if __name__ == "__main__":
    print("=" * 60)
    print("  VyaparSetu (व्यापारसेतु) · Next-Gen MSME Onboarding")
    print("  Airtel Sync 2026 Innovation Challenge (Enterprise Track A)")
    print("  Platform running on: http://localhost:8000")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
