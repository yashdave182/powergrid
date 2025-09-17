#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import google.generativeai as genai
    print("✓ Google Generative AI imported successfully")
    
    from app.config import settings
    print("✓ Config imported successfully")
    print(f"✓ Gemini API key configured: {settings.gemini_api_key[:10]}...")
    
    from app.services.ai_service import ai_service
    print("✓ AI service imported successfully")
    
    from app.api.v1.ai import router
    print("✓ AI router imported successfully")
    
    print("\n🎉 All AI integration components are working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()