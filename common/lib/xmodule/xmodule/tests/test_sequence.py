"""
Tests for sequence module.
"""

from mock import Mock
from xblock.reference.user_service import XBlockUser, UserService
from xmodule.tests import get_test_system
from xmodule.tests.xml import XModuleXmlImportTest
from xmodule.tests.xml import factories as xml
from xmodule.x_module import STUDENT_VIEW, AUTHOR_VIEW
from xmodule.seq_module import _compute_next_url


class StubUserService(UserService):
    """
    Stub UserService for testing the sequence module.
    """
    def get_current_user(self):
        """
        Implements abstract method for getting the current user.
        """
        user = XBlockUser()
        user.opt_attrs['edx-platform.username'] = 'test user'
        return user


class SequenceBlockTestCase(XModuleXmlImportTest):
    """
    Tests for the Sequence Module.
    """
    def setUp(self):
        super(XModuleXmlImportTest, self).setUp()

        course_xml = self._set_up_course_xml()
        self.course = self.process_xml(course_xml)
        self._set_up_module_system(self.course)

        for chapter_index in range(len(self.course.get_children())):
            chapter = self._set_up_block(self.course, chapter_index)
            setattr(self, 'chapter_{}'.format(chapter_index + 1), chapter)

            for sequence_index in range(len(chapter.get_children())):
                sequence = self._set_up_block(chapter, sequence_index)
                setattr(self, 'sequence_{}_{}'.format(chapter_index + 1, sequence_index + 1), sequence)

    def _set_up_course_xml(self):
        """
        Sets up and returns XML course structure.
        """
        course = xml.CourseFactory.build()

        chapter_1 = xml.ChapterFactory.build(parent=course)  # has 2 child sequences
        chapter_2 = xml.ChapterFactory.build(parent=course)  # has 0 child sequences
        chapter_3 = xml.ChapterFactory.build(parent=course)  # has 1 child sequence
        chapter_4 = xml.ChapterFactory.build(parent=course)  # has 2 child sequences

        sequence_1_1 = xml.SequenceFactory.build(parent=chapter_1)
        xml.SequenceFactory.build(parent=chapter_1)
        xml.SequenceFactory.build(parent=chapter_3)
        xml.SequenceFactory.build(parent=chapter_4)
        xml.SequenceFactory.build(parent=chapter_4)

        vertical_1_1_A = xml.VerticalFactory.build(parent=sequence_1_1)
        xml.ProblemFactory.build(parent=vertical_1_1_A)

        return course

    def _set_up_block(self, parent, index_in_parent):
        """
        Sets up the stub sequence module for testing.
        """
        block = parent.get_children()[index_in_parent]

        self._set_up_module_system(block)

        block.xmodule_runtime._services['bookmarks'] = Mock()
        block.xmodule_runtime._services['user'] = StubUserService()
        block.xmodule_runtime.xmodule_instance = block._xmodule
        block.parent = parent.location
        return block

    def _set_up_module_system(self, block):
        """
        Sets up the test module system for the given block.
        """
        module_system = get_test_system()
        module_system.descriptor_runtime = block._runtime  # pylint: disable=protected-access
        block.xmodule_runtime = module_system

    def test_render_student_view(self):
        html = self.sequence_1_1.xmodule_runtime.render(
            self.sequence_1_1,
            STUDENT_VIEW,
            {'get_redirect_url': lambda course_key, block_location, first_child: unicode(block_location)},
        ).content
        self.assertIn('Problem', html)
        self.assertIn("'next_url': u'{}'".format(unicode(self.sequence_1_2.location)), html)

    def test_compute_next_url(self):

        for sequence, parent, expected_next_sequence_location in [
            (self.sequence_1_1, self.chapter_1, self.sequence_1_2.location),
            (self.sequence_1_2, self.chapter_1, self.chapter_2.location),
            (self.sequence_3_1, self.chapter_3, self.chapter_4.location),
            (self.sequence_4_1, self.chapter_4, self.sequence_4_2.location),
            (self.sequence_4_2, self.chapter_4, None),
        ]:
            actual_next_sequence_location = _compute_next_url(
                sequence.location,
                parent,
                lambda course_key, block_location, first_child: block_location,
            )
            self.assertEquals(actual_next_sequence_location, expected_next_sequence_location)
