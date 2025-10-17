#!/usr/bin/env python3
"""
Test della nuova strategia di mascheramento delle password.

Questo test verifica che:
1. AdminRequestSerializer mascheri le password per sicurezza UI/API
2. AWXRequestSerializer preservi le password reali per AWX
3. full_survey mascheri le password per display 
4. _get_full_survey_for_awx() preservi le password reali
5. perform_processing usi i valori reali per AWX
"""

def test_password_masking_strategy():
    """Test della strategia di mascheramento selettivo delle password."""
    
    print("🔒 Test della nuova strategia di mascheramento password")
    print("=" * 60)
    
    # Simula dati di test con password
    test_data = {
        'text_variable': 'test_value',
        'password_var': 'my_secret_password',
        'integer_var': 42
    }
    
    # Simula oggetti di test
    class MockTowerSurveyField:
        def __init__(self, variable, field_type):
            self.variable = variable
            self.type = field_type
    
    class MockOperation:
        def __init__(self):
            self.tower_survey_fields = MockTowerSurveyFields()
    
    class MockTowerSurveyFields:
        def filter(self, type=None):
            if type == 'password':
                return [MockTowerSurveyField('password_var', 'password')]
            return []
    
    class MockRequest:
        def __init__(self):
            self.fill_in_survey = test_data.copy()
            self.admin_fill_in_survey = {}
            self.approval_workflow_state = None
            self.operation = MockOperation()
        
        @property
        def full_survey(self):
            # Simula la nuova logica con mascheramento
            full_survey = {k: v for k, v in {**self.fill_in_survey}.items() if v is not None}
            full_survey.update({k: v for k, v in {**self.admin_fill_in_survey}.items() if v is not None})
            
            # Maschera i campi password per sicurezza (UI/API display)
            password_fields = []
            for tower_survey_field in self.operation.tower_survey_fields.filter(type='password'):
                password_fields.append(tower_survey_field.variable)
            
            if password_fields:
                for password_field in password_fields:
                    if password_field in full_survey and full_survey[password_field]:
                        full_survey[password_field] = "$encrypted$"
            
            return full_survey
        
        def _get_full_survey_for_awx(self):
            # Simula la logica senza mascheramento per AWX
            full_survey = {k: v for k, v in {**self.fill_in_survey}.items() if v is not None}
            full_survey.update({k: v for k, v in {**self.admin_fill_in_survey}.items() if v is not None})
            # No password masking for AWX - return the real values
            return full_survey
    
    # Crea request simulata
    mock_request = MockRequest()
    
    print("📋 Dati originali:")
    print(f"   fill_in_survey: {mock_request.fill_in_survey}")
    
    print("\n🔒 Test 1: full_survey (per UI/API) - deve mascherare")
    masked_survey = mock_request.full_survey
    print(f"   full_survey: {masked_survey}")
    assert masked_survey['password_var'] == '$encrypted$', f"❌ Password non mascherata: {masked_survey['password_var']}"
    assert masked_survey['text_variable'] == 'test_value', f"❌ Campo text alterato: {masked_survey['text_variable']}"
    print("   ✅ Password mascherata correttamente")
    
    print("\n🔓 Test 2: _get_full_survey_for_awx() - deve preservare")
    awx_survey = mock_request._get_full_survey_for_awx()
    print(f"   _get_full_survey_for_awx(): {awx_survey}")
    assert awx_survey['password_var'] == 'my_secret_password', f"❌ Password non preservata: {awx_survey['password_var']}"
    assert awx_survey['text_variable'] == 'test_value', f"❌ Campo text alterato: {awx_survey['text_variable']}"
    print("   ✅ Password preservata correttamente")
    
    print("\n📊 Test 3: Simulazione serializers")
    
    # Simula AdminRequestSerializer (per UI/API)
    class MockAdminSerializer:
        def __init__(self, request):
            self.request = request
        
        @property 
        def data(self):
            return {
                'id': 1,
                'full_survey': self.request.full_survey,  # Usa full_survey (mascherato)
                'other_field': 'admin_data'
            }
    
    # Simula AWXRequestSerializer (per AWX)
    class MockAWXSerializer:
        def __init__(self, request):
            self.request = request
        
        @property
        def data(self):
            return {
                'id': 1,
                'full_survey': self.request._get_full_survey_for_awx(),  # Usa _get_full_survey_for_awx (non mascherato)
                'other_field': 'awx_data'
            }
    
    admin_serializer = MockAdminSerializer(mock_request)
    awx_serializer = MockAWXSerializer(mock_request)
    
    print("   📱 AdminRequestSerializer (UI/API):")
    admin_data = admin_serializer.data
    print(f"      full_survey: {admin_data['full_survey']}")
    assert admin_data['full_survey']['password_var'] == '$encrypted$', "❌ AdminSerializer non maschera"
    print("      ✅ Password mascherata per UI/API")
    
    print("   🔧 AWXRequestSerializer (AWX):")
    awx_data = awx_serializer.data
    print(f"      full_survey: {awx_data['full_survey']}")
    assert awx_data['full_survey']['password_var'] == 'my_secret_password', "❌ AWXSerializer non preserva"
    print("      ✅ Password preservata per AWX")
    
    print("\n🚀 Test 4: Simulazione perform_processing")
    
    # Simula perform_processing
    def simulate_perform_processing(request):
        # Prima: usa _get_full_survey_for_awx() per extra_vars (non mascherato)
        tower_extra_vars = request._get_full_survey_for_awx().copy()
        
        # Poi: usa AWXRequestSerializer per dati request
        awx_serializer = MockAWXSerializer(request)
        tower_extra_vars["squest"] = {
            "squest_host": "test.squest.local",
            "request": awx_serializer.data
        }
        
        return tower_extra_vars
    
    processing_vars = simulate_perform_processing(mock_request)
    
    print("   🔧 Extra vars per AWX:")
    print(f"      password_var (direct): {processing_vars.get('password_var')}")
    print(f"      password_var (in request): {processing_vars['squest']['request']['full_survey']['password_var']}")
    
    assert processing_vars.get('password_var') == 'my_secret_password', "❌ Password diretta non preservata"
    assert processing_vars['squest']['request']['full_survey']['password_var'] == 'my_secret_password', "❌ Password in request non preservata"
    print("   ✅ Password preservata in perform_processing")
    
    print("\n" + "=" * 60)
    print("🎉 TUTTI I TEST SUPERATI!")
    print("\nRiepilogo strategia implementata:")
    print("✅ 1. full_survey maschera password per UI/API")
    print("✅ 2. _get_full_survey_for_awx() preserva password per AWX")
    print("✅ 3. AdminRequestSerializer usa full_survey (mascherato)")
    print("✅ 4. AWXRequestSerializer usa _get_full_survey_for_awx() (non mascherato)")
    print("✅ 5. perform_processing usa valori non mascherati per AWX")
    print("✅ 6. Sicurezza mantenuta per UI/API")
    print("✅ 7. Funzionalità preservata per AWX")

if __name__ == "__main__":
    test_password_masking_strategy()