"""
Test migrations instructor_task table.
"""
# pylint: disable=attribute-defined-outside-init
import json

from common.test.test_migrations.utils import TestMigrations
from django.contrib.auth.models import User
from lms.djangoapps.instructor_task.models import InstructorTask
from opaque_keys.edx.keys import CourseKey

TEST_COURSE_KEY = CourseKey.from_string('course-v1:edX+1.23x+test_course')


class TestTextFields(TestMigrations):
    """
    Test migration no. 0002_auto_20160208_0810 for InstructorTask model.
    Fields changes from CharField to TextField.
    """
    migrate_from = '0001_initial'
    migrate_to = '0002_auto_20160208_0810'
    app = 'instructor_task'

    def setUpBeforeMigration(self):
        """
        Setup before migration create InstructorTask model entry to verify after migration.
        """
        self.task_input = 'x' * 250
        self.task_output = 'x' * 999
        self.instructor = User.objects.create(username="instructor", email="instructor@edx.org")
        self.task = InstructorTask.create(
            TEST_COURSE_KEY,
            "dummy type",
            "dummy key",
            self.task_input,
            self.instructor
        )
        self.task.task_output = self.task_output
        self.task.save_now()

    def test_text_fields_migrated(self):
        """
        Verify that data does not loss after migration when model field changes
        from CharField to TextField.
        """
        self.migrate_forwards()
        task_after_migration = InstructorTask.objects.get(id=self.task.id)
        self.assertEqual(task_after_migration.task_input, json.dumps(self.task_input))
        self.assertEqual(task_after_migration.task_output, self.task_output)

    def test_text_fields_migrated_store_large_data(self):
        """
        Verify that TextField changed can now store more than 255 characters.
        """
        self.migrate_forwards()
        self.task_input = 'x' * 850
        self.task = InstructorTask.create(
            TEST_COURSE_KEY,
            "dummy type",
            "dummy key",
            self.task_input,
            self.instructor
        )
        self.assertEqual(self.task.task_input, json.dumps(self.task_input))
        self.migrate_backwards()
        task_after_backward_migration = InstructorTask.objects.get(id=self.task.id)
        self.assertEqual(task_after_backward_migration.task_input, json.dumps(self.task_input))
