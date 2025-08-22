#!/usr/bin/env python3
import asyncio
import aiohttp
import json

async def test_api():
    print("🧪 Probando API de Render_QM...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health
            async with session.get("http://localhost:8000/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Health check: {data['status']}")
                else:
                    print(f"❌ Health check falló: {resp.status}")
                    return
            
            # Test login
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            async with session.post(
                "http://localhost:8000/api/v1/auth/login",
                data=login_data
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    token = data["access_token"]
                    print("✅ Login exitoso")
                    
                    # Test authenticated endpoint
                    headers = {"Authorization": f"Bearer {token}"}
                    async with session.get(
                        "http://localhost:8000/api/v1/settings/",
                        headers=headers
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            print(f"✅ Settings: {data['app_name']} v{data['version']}")
                        else:
                            print(f"❌ Settings falló: {resp.status}")
                else:
                    print(f"❌ Login falló: {resp.status}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de que el servidor esté ejecutándose")

if __name__ == "__main__":
    asyncio.run(test_api())
