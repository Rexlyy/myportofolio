from django.test import override_settings
from django.contrib.auth.models import User, Permission

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from main.models import Skill


class SkillAPITestCase(APITestCase):

    def setUp(self):
        # Membuat akun pengujian
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        self.admin = User.objects.create_superuser(
            username='testadmin',
            password='adminpassword123',
            email='admin@example.com'
        )

        # Membuat data Skill untuk pengujian
        self.skill = Skill.objects.create(
            name='Python',
            category='Programming Language',
            proficiency=85,
            description='Python programming language.',
            user=self.admin
        )

        self.client = APIClient()

        # Membuat akun Editor
        self.editor = User.objects.create_user(
            username='testeditor',
            password='editorpassword123'
        )

        # Memberikan permission change_skill kepada Editor
        change_skill_permission = Permission.objects.get(
            codename='change_skill',
            content_type__app_label='main'
        )

        self.editor.user_permissions.add(change_skill_permission)

    # ==============================
    # GET SKILL
    # ==============================

    def test_get_skill_list(self):
        response = self.client.get('/api/v1/skills/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertGreaterEqual(len(response.data), 1)

    def test_get_skill_detail(self):
        response = self.client.get(
            f'/api/v1/skills/{self.skill.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['name'],
            'Python'
        )

    def test_search_skill(self):
        response = self.client.get(
            '/api/v1/skills/?name=Python'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertGreaterEqual(len(response.data), 1)

    def test_get_nonexistent_skill(self):
        response = self.client.get(
            '/api/v1/skills/99999/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # ==============================
    # CREATE SKILL
    # ==============================

    def test_create_skill_as_admin(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': 'Java',
            'category': 'Programming Language',
            'proficiency': 90,
            'description': 'Java programming language.'
        }

        response = self.client.post(
            '/api/v1/skills/',
            data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Skill.objects.filter(name='Java').exists()
        )

    def test_create_skill_as_guest(self):
        data = {
            'name': 'Java',
            'category': 'Programming Language',
            'proficiency': 90,
            'description': 'Java programming language.'
        }

        response = self.client.post(
            '/api/v1/skills/',
            data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_create_skill_invalid_data(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': '',
            'category': 'Programming Language',
            'proficiency': 90,
            'description': 'Java programming language.'
        }

        response = self.client.post(
            '/api/v1/skills/',
            data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==============================
    # UPDATE SKILL
    # ==============================

    def test_update_skill(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': 'Python Updated'
        }

        response = self.client.patch(
            f'/api/v1/skills/{self.skill.id}/',
            data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.skill.refresh_from_db()

        self.assertEqual(
            self.skill.name,
            'Python Updated'
        )

    # ==============================
    # DELETE SKILL
    # ==============================

    def test_delete_skill(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            f'/api/v1/skills/{self.skill.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Skill.objects.filter(id=self.skill.id).exists()
        )

    # ==============================
    # STAR / UNSTAR SKILL
    # ==============================

    def test_star_skill(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/v1/skills/{self.skill.id}/star/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            self.skill.starred_by.filter(id=self.user.id).exists()
        )

    def test_unstar_skill(self):
        self.skill.starred_by.add(self.user)

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/v1/skills/{self.skill.id}/star/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertFalse(
            self.skill.starred_by.filter(id=self.user.id).exists()
        )


    # ==========================================
    # ROLE-BASED PERMISSION TESTING
    # ==========================================

    def test_create_skill_as_normal_user(self):
        # User biasa mencoba membuat Skill
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'Java',
            'category': 'Programming Language',
            'proficiency': 90,
            'description': 'Java programming language.'
        }

        response = self.client.post(
            '/api/v1/skills/',
            data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertFalse(
            Skill.objects.filter(name='Java').exists()
        )

    def test_update_skill_as_normal_user(self):
        # User biasa mencoba mengedit Skill
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f'/api/v1/skills/{self.skill.id}/',
            {'name': 'Hacked Python'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.skill.refresh_from_db()

        self.assertEqual(self.skill.name, 'Python')

    def test_delete_skill_as_normal_user(self):
        # User biasa mencoba menghapus Skill
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/v1/skills/{self.skill.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertTrue(
            Skill.objects.filter(id=self.skill.id).exists()
        )

    def test_update_skill_as_editor(self):
        # Editor memiliki permission change_skill
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(
            f'/api/v1/skills/{self.skill.id}/',
            {'name': 'Python Edited by Editor'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.skill.refresh_from_db()

        self.assertEqual(
            self.skill.name,
            'Python Edited by Editor'
        )

    def test_delete_skill_as_editor(self):
        # Editor tidak boleh menghapus Skill
        self.client.force_authenticate(user=self.editor)

        response = self.client.delete(
            f'/api/v1/skills/{self.skill.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertTrue(
            Skill.objects.filter(id=self.skill.id).exists()
        )

    def test_create_skill_as_editor(self):
        # Editor tidak boleh membuat Skill
        self.client.force_authenticate(user=self.editor)

        data = {
            'name': 'C++',
            'category': 'Programming Language',
            'proficiency': 85,
            'description': 'C++ programming language.'
        }

        response = self.client.post(
            '/api/v1/skills/',
            data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertFalse(
            Skill.objects.filter(name='C++').exists()
        )

    def test_guest_cannot_star_skill(self):
        # Guest mencoba melakukan Star
        response = self.client.post(
            f'/api/v1/skills/{self.skill.id}/star/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertFalse(
            self.skill.starred_by.exists()
        )

    def test_denied_operation_does_not_change_database(self):
        # User biasa mencoba mengubah Skill
        self.client.force_authenticate(user=self.user)

        original_count = Skill.objects.count()
        original_name = self.skill.name

        response = self.client.patch(
            f'/api/v1/skills/{self.skill.id}/',
            {'name': 'Unauthorized Change'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.skill.refresh_from_db()

        # Memastikan database tidak berubah
        self.assertEqual(self.skill.name, original_name)
        self.assertEqual(Skill.objects.count(), original_count)

    # ==========================================
    # CSRF TESTING
    # ==========================================

    def test_create_skill_without_csrf_token(self):
        # Client dengan pemeriksaan CSRF aktif
        csrf_client = APIClient(enforce_csrf_checks=True)

        # Login sebagai Admin menggunakan session
        csrf_client.login(
            username='testadmin',
            password='adminpassword123'
        )

        data = {
            'name': 'JavaScript',
            'category': 'Programming Language',
            'proficiency': 90,
            'description': 'JavaScript programming language.'
        }

        # POST tanpa CSRF token
        response = csrf_client.post(
            '/api/v1/skills/',
            data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        # Pastikan data tidak masuk database
        self.assertFalse(
            Skill.objects.filter(name='JavaScript').exists()
        )

    def test_update_skill_without_csrf_token(self):
        # Client dengan pemeriksaan CSRF aktif
        csrf_client = APIClient(enforce_csrf_checks=True)

        # Login sebagai Admin menggunakan session
        csrf_client.login(
            username='testadmin',
            password='adminpassword123'
        )

        # PATCH tanpa CSRF token
        response = csrf_client.patch(
            f'/api/v1/skills/{self.skill.id}/',
            {'name': 'Unauthorized Update'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        # Pastikan data tidak berubah
        self.skill.refresh_from_db()

        self.assertEqual(
            self.skill.name,
            'Python'
        )