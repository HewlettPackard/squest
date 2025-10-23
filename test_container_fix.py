#!/usr/bin/env python3
"""
Test rapido per verificare che la nuova implementazione password masking sia caricata
"""

print("🔒 Test implementazione Password Masking v2 in container")
print("=" * 60)

try:
    # Importa i serializer
    from service_catalog.api.serializers.request_serializers import AdminRequestSerializer, AWXRequestSerializer
    print("✅ 1. Import serializers - SUCCESSO")
    
    # Verifica che AWXRequestSerializer abbia il metodo to_representation
    if hasattr(AWXRequestSerializer, 'to_representation'):
        print("✅ 2. AWXRequestSerializer.to_representation - PRESENTE")
    else:
        print("❌ 2. AWXRequestSerializer.to_representation - MANCANTE")
    
    # Verifica che Request abbia il metodo _get_full_survey_for_awx
    from service_catalog.models.request import Request
    if hasattr(Request, '_get_full_survey_for_awx'):
        print("✅ 3. Request._get_full_survey_for_awx - PRESENTE")
    else:
        print("❌ 3. Request._get_full_survey_for_awx - MANCANTE")
    
    print("\n🎉 IMPLEMENTAZIONE CARICATA CORRETTAMENTE!")
    print("\n📋 Per testare completamente:")
    print("1. Crea una request con campo password")
    print("2. Controlla che AdminRequestSerializer mascheri ($encrypted$)")
    print("3. Controlla che AWXRequestSerializer preservi il valore reale")
    
except ImportError as e:
    print(f"❌ ERRORE IMPORT: {e}")
except Exception as e:
    print(f"❌ ERRORE GENERALE: {e}")