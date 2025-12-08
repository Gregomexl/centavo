#!/usr/bin/env python3
"""Test script for authentication API."""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"


async def test_health():
    """Test health endpoint."""
    print("🔍 Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"✅ Health: {response.json()}")
        return response.status_code == 200


async def test_register():
    """Test user registration."""
    print("\n🔍 Testing user registration...")
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "display_name": "Test User"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
        if response.status_code == 201:
            print(f"✅ Register: {response.json()}")
            return response.json()
        else:
            print(f"❌ Register failed: {response.status_code} - {response.text}")
            return None


async def test_login():
    """Test user login."""
    print("\n🔍 Testing user login...")
    credentials = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/api/v1/auth/login", json=credentials)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"   Access token: {data['access_token'][:50]}...")
            print(f"   Refresh token: {data['refresh_token'][:50]}...")
            return data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None


async def test_get_me(access_token: str):
    """Test getting current user."""
    print("\n🔍 Testing /auth/me endpoint...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        if response.status_code == 200:
            print(f"✅ Get current user: {response.json()}")
            return True
        else:
            print(f"❌ Get me failed: {response.status_code} - {response.text}")
            return False


async def main():
    """Run all tests."""
    print("🚀 Starting Authentication API Tests\n")
    print("=" * 60)
    
    try:
        # Test health
        if not await test_health():
            print("\n❌ Server is not healthy. Make sure it's running!")
            return
        
        # Test register
        user = await test_register()
        
        # Test login
        access_token = await test_login()
        if not access_token:
            return
        
        # Test protected endpoint
        await test_get_me(access_token)
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        
    except httpx.ConnectError:
        print("\n❌ Could not connect to server. Is it running at http://localhost:8000?")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
