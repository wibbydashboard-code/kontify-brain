
import requests
import json

def test_autotransporte_api():
    try:
        response = requests.get("http://localhost:5000/api/questions/autotransporte")
        if response.status_code == 200:
            questions = response.json()
            print(f"✅ Received {len(questions)} questions.")
            
            # Check the first question
            q1 = questions[0]
            print(f"Q1: {q1['q']}")
            print(f"Options: {q1['options']}")
            
            if len(q1['options']) > 2 and "Régimen de Coordinados" in q1['options']:
                print("✅ Q1 has more than 2 options including 'Régimen de Coordinados'.")
            else:
                print("❌ Q1 does not match expected criteria.")
                
            # Check a binary question (e.g. Q3)
            q3 = questions[2] # Index 2
            print(f"Q3: {q3['q']}")
            print(f"Options: {q3['options']}")
            if len(q3['options']) == 2:
                print("✅ Q3 is binary (SÍ/NO).")
            else:
                print("❌ Q3 is not binary.")
                
        else:
            print(f"❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_autotransporte_api()
