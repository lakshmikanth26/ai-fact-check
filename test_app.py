#!/usr/bin/env python3
"""
Simple test script to verify the fact-checking functionality.
Run this to test the core components before starting the web server.
"""

import sys
import json
from factcheck import FactChecker

def test_wikipedia_search():
    """Test Wikipedia search functionality."""
    print("🔍 Testing Wikipedia search...")
    
    fact_checker = FactChecker()
    articles = fact_checker.search_wikipedia("water boiling point", limit=2)
    
    if articles:
        print(f"✅ Found {len(articles)} articles")
        for article in articles:
            print(f"   - {article['title']}: {article['description']}")
        return True
    else:
        print("❌ No articles found")
        return False

def test_fact_checking():
    """Test the complete fact-checking pipeline."""
    print("\n🧠 Testing fact-checking pipeline...")
    
    fact_checker = FactChecker()
    test_claim = "Water boils at 100 degrees Celsius at sea level"
    
    try:
        result = fact_checker.fact_check(test_claim)
        
        print(f"✅ Fact-check completed")
        print(f"   Claim: {result['claim']}")
        print(f"   Classification: {result['classification']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Sources: {len(result['sources'])} found")
        
        return True
    except Exception as e:
        print(f"❌ Fact-check failed: {e}")
        return False

def test_caching():
    """Test the caching system."""
    print("\n💾 Testing caching system...")
    
    fact_checker = FactChecker()
    test_claim = "The Earth is round"
    
    # First call (should cache)
    result1 = fact_checker.fact_check(test_claim)
    
    # Second call (should use cache)
    result2 = fact_checker.fact_check(test_claim)
    
    if result1['classification'] == result2['classification']:
        print("✅ Caching working correctly")
        return True
    else:
        print("❌ Caching issue detected")
        return False

def test_flask_app():
    """Test Flask app initialization."""
    print("\n🌐 Testing Flask app...")
    
    try:
        from app import app
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Main page loads correctly")
            else:
                print(f"❌ Main page error: {response.status_code}")
                return False
            
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint error: {response.status_code}")
                return False
            
            # Test chat endpoint
            response = client.post('/chat', 
                                 json={'message': 'Test claim'},
                                 content_type='application/json')
            if response.status_code == 200:
                print("✅ Chat endpoint working")
                return True
            else:
                print(f"❌ Chat endpoint error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Fact-Check Chatbot Tests\n")
    
    tests = [
        ("Wikipedia Search", test_wikipedia_search),
        ("Fact Checking", test_fact_checking),
        ("Caching System", test_caching),
        ("Flask App", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The chatbot is ready to use.")
        print("\nTo start the web server, run:")
        print("   python app.py")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
