#!flask/bin/python
import os
import unittest
from config import basedir
from app import app, db
from app.models import ImageRequest, READY, NOT_READY
from app.views import allowed_file, change_img_size
from PIL import Image


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        self.app_context.pop()
        db.session.remove()
        db.drop_all()

    def test_allowed_file(self):
        filenames = [
            '12345.png',
            'image.jpg',
            'chris_why_.gif',
            'Shin.Megami.Tensei_.PERSONA.5.full.2090418.jpg',
            '2CJ1_qhSDMw.jpg',
            'lane2013 (1).pdf',
            'горы_стена.png',
            'index.html',
            'arrow_prev.svg']
        results = [
            True,
            True,
            False,
            True,
            True,
            False,
            True,
            False,
            False
        ]
        for i in range(0, len(filenames)):
            assert allowed_file(filenames[i]) == results[i]

    def test_change_img_size(self):
        new_record = ImageRequest(w=100, h=100, img_path='test.png')
        db.session.add(new_record)
        db.session.commit()
        change_img_size('test.png', 100, 100, new_record.id)
        assert new_record.status == READY
        result = Image.open('app/static/test.png')
        assert result.size == (100, 100)

    def test_task_status(self):
        rv = self.app.get(
            '/status/4242'
        )
        self.assertEqual(rv.status_code, 404)

        new_record = ImageRequest(w=100, h=100, img_path='test.png')
        db.session.add(new_record)
        db.session.commit()
        rv = self.app.get(
            '/status/1'
        )
        self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
