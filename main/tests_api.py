
from django.contrib.auth.models import User
from django.urls import reverse

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

    def test_get_skill_list(self):
        response = self.client.get('/api/skills-drf/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertGreaterEqual(len(response.data), 1)

    def test_get_skill_detail(self):
        response = self.client.get(
            f'/api/skills-drf/{self.skill.id}/'
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
            '/api/skills-drf/?name=Python'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertGreaterEqual(len(response.data), 1)

    def test_get_nonexistent_skill(self):
        response = self.client.get(
            '/api/skills-drf/99999/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )


    def test_create_skill_as_admin(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': 'Java',
            'category': 'Programming Language',
            'proficiency': 90,
            'description': 'Java programming language.'
        }

        response = self.client.post('/api/skills-drf/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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

        response = self.client.post('/api/skills-drf/', data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_skill_invalid_data(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': '',
            'category': 'Programming Language',
            'proficiency': 90,
            'description': 'Java programming language.'
        }

        response = self.client.post('/api/skills-drf/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_skill(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': 'Python Updated'
        }

        response = self.client.patch(
            f'/api/skills-drf/{self.skill.id}/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, 'Python Updated')

    def test_delete_skill(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            f'/api/skills-drf/{self.skill.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Skill.objects.filter(id=self.skill.id).exists()
        )

    def test_star_skill(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/skills-drf/{self.skill.id}/star/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            self.skill.starred_by.filter(id=self.user.id).exists()
        )

    def test_unstar_skill(self):
        self.skill.starred_by.add(self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/skills-drf/{self.skill.id}/star/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            self.skill.starred_by.filter(id=self.user.id).exists()
        )
