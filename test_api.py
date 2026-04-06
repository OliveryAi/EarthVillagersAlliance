#!/usr/bin/env python
"""API 功能测试脚本 - Token 认证方式"""
import requests
import os

BASE_URL = "http://127.0.0.1:8000/api"


def test_company_search():
    """测试企业查询 API"""
    print("\n[TEST] 企业搜索功能")
    response = requests.get(f"{BASE_URL}/vote/companies/search/?q=Tencent")
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Found {len(data)} companies")
        for c in data[:3]:
            print(f"  - {c['name']} ({c['industry']}, {c['city']})")
    else:
        print(f"[FAIL] Status code: {response.status_code}")


def test_ranking():
    """测试榜单查询 API"""
    print("\n[TEST] 榜单排行功能")
    response = requests.get(f"{BASE_URL}/vote/ranking/age_discrimination/")
    if response.status_code == 200:
        data = response.json()
        if 'rankings' in data:
            print(f"[OK] {data['category_name']} retrieved")
            for r in data['rankings'][:5]:
                print(f"  #{r['rank']} {r['company_name']} - {r['vote_rate']:.2f}%")
        else:
            print("[FAIL] Unexpected format")
    else:
        print(f"[FAIL] Status code: {response.status_code}")


def test_all_rankings():
    """测试所有榜单查询"""
    print("\n[TEST] 所有榜单列表")
    response = requests.get(f"{BASE_URL}/vote/ranking/")
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Retrieved {len(data)} rankings total")


def test_vote_submission():
    """测试投票提交 API - Token 认证方式"""
    print("\n[TEST] 投票提交功能 (Token Authentication)")

    session = requests.Session()

    # 登录获取 token
    login_response = session.post(f"{BASE_URL}/auth/login/", {
        'username': 'testuser',
        'password': 'TestPass123!'
    })

    if login_response.status_code != 200:
        print(f"[FAIL] Login failed, status: {login_response.status_code}")
        return

    login_data = login_response.json()
    token = login_data.get('token')

    if not token:
        print("[FAIL] No token in response")
        return

    print(f"[OK] Logged in, got token: {token[:16]}...")

    # 获取企业 ID
    search_response = session.get(f"{BASE_URL}/vote/companies/search/?q=Tencent")
    if search_response.status_code != 200:
        print("[FAIL] Cannot find company for voting test")
        return

    companies = search_response.json()
    if not companies:
        print("[FAIL] No companies found for testing")
        return

    company_id = companies[0]['id']
    print(f"[OK] Found company ID {company_id}: {companies[0]['name']}")

    # 提交投票（Token header）
    headers = {
        'Authorization': f'Token {token}',
    }

    response = session.post(f"{BASE_URL}/vote/submit/", {
        'category': 'age_discrimination',
        'company_id': company_id,
        'reason': 'Test voting for employment discrimination at age 35+'
    }, headers=headers)

    if response.status_code == 201:
        result = response.json()
        print(f"[OK] Vote submitted successfully")
        print(f"  - Vote ID: {result.get('vote_id')}")
        print(f"  - Remaining today: {result.get('remaining_today')}")

    elif response.status_code == 400:
        error = response.json().get('error', 'Unknown error')
        if '已对该企业' in str(error):
            print("[OK] Vote already exists (expected behavior)")
        else:
            print(f"[WARN] Duplicate vote prevented: {error}")

    elif response.status_code == 403:
        print(f"[FAIL] 403 Forbidden. Response: {response.text}")

    else:
        print(f"[FAIL] Status code: {response.status_code}, Response: {response.text}")


def test_vote_fraud_detection():
    """测试防刷票机制"""
    print("\n[TEST] 防刷票机制 - 重复投票检测")

    session = requests.Session()
    login_response = session.post(f"{BASE_URL}/auth/login/", {
        'username': 'testuser',
        'password': 'TestPass123!'
    })

    if login_response.status_code != 200:
        print("[FAIL] Login failed")
        return

    token = login_response.json().get('token')
    headers = {'Authorization': f'Token {token}'}

    search_response = session.get(f"{BASE_URL}/vote/companies/search/?q=Tencent")
    companies = search_response.json()

    if not companies:
        print("[FAIL] No companies for testing")
        return

    company_id = companies[0]['id']

    # 尝试第二次相同投票（应该失败）
    response = session.post(f"{BASE_URL}/vote/submit/", {
        'category': 'age_discrimination',
        'company_id': company_id,
        'reason': 'Second vote attempt'
    }, headers=headers)

    if response.status_code == 400:
        error = response.json().get('error', '')
        if '已对该企业' in str(error):
            print(f"[OK] Anti-fraud detected: {error}")
        else:
            print(f"[WARN] Different error: {error}")
    elif response.status_code == 201:
        print("[FAIL] Duplicate voting not prevented - security issue!")
    else:
        print(f"[FAIL] Unexpected status: {response.status_code}, Response: {response.text}")


def test_evidence_upload():
    """测试证据上传"""
    print("\n[TEST] 证据材料上传")

    session = requests.Session()
    login_response = session.post(f"{BASE_URL}/auth/login/", {
        'username': 'testuser',
        'password': 'TestPass123!'
    })

    if login_response.status_code != 200:
        print("[FAIL] Login failed")
        return

    token = login_response.json().get('token')
    headers = {
        'Authorization': f'Token {token}',
    }

    search_response = session.get(f"{BASE_URL}/vote/companies/search/?q=Tencent")
    companies = search_response.json()

    if not companies:
        print("[FAIL] No companies for testing")
        return

    company_id = companies[0]['id']

    # 先投一票
    vote_response = session.post(f"{BASE_URL}/vote/submit/", {
        'category': 'age_discrimination',
        'company_id': company_id,
        'reason': 'Vote before evidence upload'
    }, headers=headers)

    if vote_response.status_code != 201:
        print("[WARN] Cannot submit test vote for evidence upload")
        return

    vote_id = vote_response.json().get('vote_id')
    print(f"[OK] Vote created: {vote_id}")

    # 尝试上传证据（没有文件，应该失败）
    response = session.post(
        f"{BASE_URL}/evidence/upload/",
        data={'vote_id': vote_id},
        headers=headers
    )

    if response.status_code == 400:
        print(f"[OK] Evidence upload correctly failed without file")


if __name__ == '__main__':
    test_company_search()
    test_ranking()
    test_all_rankings()
    test_vote_submission()
    test_vote_fraud_detection()
    test_evidence_upload()
    print("\n=== API Tests Complete ===")
