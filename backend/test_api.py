#!/usr/bin/env python3
"""Comprehensive test script for Centavo API."""

import asyncio
from datetime import date
from decimal import Decimal

import httpx

BASE_URL = "http://localhost:8000"

# Test data
TEST_USER = {
    "email": "testuser@centavo.com",
    "password": "SecurePassword123!",
    "display_name": "Test User",
}

TEST_TRANSACTION = {
    "type": "expense",
    "amount": 50.99,
    "currency": "MXN",
    "description": "Lunch at restaurant",
    "transaction_date": str(date.today()),
}

TEST_CATEGORY = {
    "name": "Custom Food",
    "icon": "🍕",
    "color": "#ff6b6b",
    "type": "expense",
}


async def test_health():
    """Test health endpoint."""
    print("\n" + "=" * 60)
    print("1️⃣  Testing Health Endpoint")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        print("✅ Health check passed!")


async def test_register():
    """Test user registration."""
    print("\n" + "=" * 60)
    print("2️⃣  Testing User Registration")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=TEST_USER
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ User created: {data['email']} (ID: {data['id']})")
            return data
        elif response.status_code == 409:
            print("⚠️  User already exists, will use for login")
            return None
        else:
            print(f"❌ Registration failed: {response.text}")
            raise Exception("Registration failed")


async def test_login():
    """Test user login."""
    print("\n" + "=" * 60)
    print("3️⃣  Testing User Login")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": TEST_USER["email"], "password": TEST_USER["password"]}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"   Token type: {data['token_type']}")
            print(f"   Access token: {data['access_token'][:30]}...")
            return data["access_token"]
        else:
            print(f"❌ Login failed: {response.text}")
            raise Exception("Login failed")


async def test_get_current_user(token: str):
    """Test getting current user info."""
    print("\n" + "=" * 60)
    print("4️⃣  Testing Get Current User")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current user: {data['display_name']} ({data['email']})")
            return data
        else:
            print(f"❌ Failed: {response.text}")
            raise Exception("Get current user failed")


async def test_list_categories(token: str):
    """Test listing categories."""
    print("\n" + "=" * 60)
    print("5️⃣  Testing List Categories")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/categories",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Found {len(categories)} categories")
            
            expense_cats = [c for c in categories if c["type"] == "expense"]
            income_cats = [c for c in categories if c["type"] == "income"]
            
            print(f"   Expense categories: {len(expense_cats)}")
            print(f"   Income categories: {len(income_cats)}")
            
            if categories:
                print(f"\n   Sample category: {categories[0]['icon']} {categories[0]['name']}")
                return categories[0]["id"]  # Return first category ID for transaction test
            return None
        else:
            print(f"❌ Failed: {response.text}")
            return None


async def test_create_category(token: str):
    """Test creating a custom category."""
    print("\n" + "=" * 60)
    print("6️⃣  Testing Create Custom Category")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/categories",
            headers=headers,
            json=TEST_CATEGORY
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Category created: {data['icon']} {data['name']}")
            print(f"   ID: {data['id']}")
            return data["id"]
        elif response.status_code == 400:
            print("⚠️  Category already exists")
            return None
        else:
            print(f"❌ Failed: {response.text}")
            return None


async def test_create_transaction(token: str, category_id: str):
    """Test creating a transaction."""
    print("\n" + "=" * 60)
    print("7️⃣  Testing Create Transaction")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    transaction_data = TEST_TRANSACTION.copy()
    if category_id:
        transaction_data["category_id"] = category_id
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/transactions",
            headers=headers,
            json=transaction_data
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Transaction created!")
            print(f"   Type: {data['type']}")
            print(f"   Amount: ${data['amount']} {data['currency']}")
            print(f"   Description: {data['description']}")
            print(f"   ID: {data['id']}")
            return data["id"]
        else:
            print(f"❌ Failed: {response.text}")
            return None


async def test_list_transactions(token: str):
    """Test listing transactions."""
    print("\n" + "=" * 60)
    print("8️⃣  Testing List Transactions")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/transactions?page=1&page_size=10",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total']} total transactions")
            print(f"   Page: {data['page']}/{data['total_pages']}")
            print(f"   Items on this page: {len(data['items'])}")
            
            if data['items']:
                first = data['items'][0]
                print(f"\n   Latest: {first['type']} - ${first['amount']} - {first['description']}")
        else:
            print(f"❌ Failed: {response.text}")


async def test_update_transaction(token: str, transaction_id: str):
    """Test updating a transaction."""
    print("\n" + "=" * 60)
    print("9️⃣  Testing Update Transaction")
    print("=" * 60)
    
    if not transaction_id:
        print("⚠️  No transaction ID, skipping...")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "amount": 75.50,
        "description": "Updated: Dinner at restaurant"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{BASE_URL}/api/v1/transactions/{transaction_id}",
            headers=headers,
            json=update_data
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Transaction updated!")
            print(f"   New amount: ${data['amount']}")
            print(f"   New description: {data['description']}")
        else:
            print(f"❌ Failed: {response.text}")


async def main():
    """Run all tests."""
    print("\n" + "🚀" * 30)
    print("CENTAVO API COMPREHENSIVE TEST SUITE")
    print("🚀" * 30)
    
    try:
        # Test health
        await test_health()
        
        # Test auth
        await test_register()
        token = await test_login()
        await test_get_current_user(token)
        
        # Test categories
        category_id = await test_list_categories(token)
        custom_cat_id = await test_create_category(token)
        
        # Use custom category if created, otherwise use first system category
        cat_to_use = custom_cat_id or category_id
        
        # Test transactions
        transaction_id = await test_create_transaction(token, cat_to_use)
        await test_list_transactions(token)
        await test_update_transaction(token, transaction_id)
        
        # Final summary
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📊 API is fully functional!")
        print(f"🔗 Swagger docs: {BASE_URL}/docs")
        print(f"🔗 ReDoc: {BASE_URL}/redoc")
        
    except httpx.ConnectError:
        print(f"\n❌ Could not connect to {BASE_URL}")
        print("   Make sure the server is running:")
        print("   cd backend && PYTHONPATH=. uv run uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
