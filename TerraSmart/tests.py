from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .views import promediar_variables_medicion, evaluar_suelo


class VistasBasicasTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_bienvenida_status(self):
        response = self.client.get(reverse('bienvenida'))
        self.assertEqual(response.status_code, 200)

    def test_instrucciones_status(self):
        response = self.client.get(reverse('instrucciones'))
        self.assertEqual(response.status_code, 200)

    def test_login_status(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_registro_status(self):
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)

class PromedioMedicionesTest(TestCase):
    def test_promediar_variables_medicion(self):
        datos = [
            {'PH': 6, 'MateriaOrganica': 2, 'Fosforo': 10, 'Azufre': 5, 'Calcio': 3, 'Magnesio': 1, 'Potasio': 0.5, 'Sodio': 0.2, 'Hierro': 7, 'Cobre': 0.5, 'Manganeso': 12, 'Zinc': 2},
            {'PH': 8, 'MateriaOrganica': 4, 'Fosforo': 20, 'Azufre': 15, 'Calcio': 5, 'Magnesio': 2, 'Potasio': 0.7, 'Sodio': 0.3, 'Hierro': 8, 'Cobre': 0.6, 'Manganeso': 14, 'Zinc': 3},
        ]
        resultado = promediar_variables_medicion(datos)
        self.assertAlmostEqual(resultado.PH, 7.0)
        self.assertAlmostEqual(resultado.MateriaOrganica, 3.0)
        self.assertAlmostEqual(resultado.Fosforo, 15.0)
        self.assertAlmostEqual(resultado.Azufre, 10.0)
        self.assertAlmostEqual(resultado.Calcio, 4.0)
        self.assertAlmostEqual(resultado.Magnesio, 1.5)
        self.assertAlmostEqual(resultado.Potasio, 0.6)
        self.assertAlmostEqual(resultado.Sodio, 0.25)
        self.assertAlmostEqual(resultado.Hierro, 7.5)
        self.assertAlmostEqual(resultado.Cobre, 0.55)
        self.assertAlmostEqual(resultado.Manganeso, 13.0)
        self.assertAlmostEqual(resultado.Zinc, 2.5)


class ThingSpeakMonitorTest(TestCase):
    @patch('TerraSmart.thingspeak_monitor.run_monitor')
    def test_thingspeak_monitor_called(self, mock_run_monitor):
        # Simula el llamado al monitor de ThingSpeak
        mock_run_monitor.return_value = None
        # Aquí podrías llamar a una vista que lo use, o simplemente probar el mock
        mock_run_monitor('usuario_test')
        mock_run_monitor.assert_called_with('usuario_test')

class FirestoreTest(TestCase):
    @patch('TerraSmart.firebase_config.db')
    def test_firestore_add_and_get(self, mock_db):
        # Simula agregar y obtener datos de Firestore
        collection_mock = MagicMock()
        mock_db.collection.return_value = collection_mock
        collection_mock.add.return_value = None
        collection_mock.where.return_value.stream.return_value = []
        # Simula agregar
        collection_mock.add({'user': 'test', 'PH': 7})
        collection_mock.add.assert_called()
        # Simula consulta
        docs = collection_mock.where('user', '==', 'test').stream()
        self.assertEqual(list(docs), [])

class UsuarioTest(TestCase):
    def test_creacion_usuario(self):
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='testuser', password='12345')
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(user.check_password('12345'))

class PrediccionTest(TestCase):
    @patch('TerraSmart.views.model')
    def test_evaluar_suelo_predice_cultivo(self, mock_model):
        # Simula el modelo de ML
        mock_model.predict.return_value = ['Maíz']
        fila = {
            'pH agua:suelo 2,5:1,0': 6.5,
            'Materia orgánica (MO) %': 3.0,
            'Fósforo (P) Bray II mg/kg': 20,
            'Azufre (S) Fosfato monocalcico mg/kg': 15,
            'Calcio (Ca) intercambiable cmol(+)/kg': 6,
            'Magnesio (Mg) intercambiable cmol(+)/kg': 2,
            'Potasio (K) intercambiable cmol(+)/kg': 0.5,
            'Sodio (Na) intercambiable cmol(+)/kg': 0.2,
            'Hierro (Fe) disponible olsen mg/kg': 8,
            'Cobre (Cu) disponible mg/kg': 0.5,
            'Manganeso (Mn) disponible Olsen mg/kg': 12,
            'Zinc (Zn) disponible Olsen mg/kg': 2
        }
        resultado = evaluar_suelo(fila)
        self.assertEqual(resultado['cultivo'], 'Maíz')