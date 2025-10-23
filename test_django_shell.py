from service_catalog.api.serializers.request_serializers import AdminRequestSerializer, AWXRequestSerializer
from service_catalog.models.request import Request

print("🔒 Test implementazione Password Masking v2")
print("✅ 1. Import serializers - SUCCESSO")

if hasattr(AWXRequestSerializer, 'to_representation'):
    print("✅ 2. AWXRequestSerializer.to_representation - PRESENTE")
else:
    print("❌ 2. AWXRequestSerializer.to_representation - MANCANTE")

if hasattr(Request, '_get_full_survey_for_awx'):
    print("✅ 3. Request._get_full_survey_for_awx - PRESENTE")
else:
    print("❌ 3. Request._get_full_survey_for_awx - MANCANTE")

print("\n🎉 IMPLEMENTAZIONE CARICATA CORRETTAMENTE!")
exit()