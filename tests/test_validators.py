from unittest import TestCase

from meetups.validators import OptionalIf
from wtforms.validators import StopValidation


# The Dummy* classes are borrowed from tests.validators in wtforms
class DummyTranslations(object):
    def gettext(self, string):
        return string

    def ngettext(self, singular, plural, n):
        if n == 1:
            return singular

        return plural


class DummyForm(dict):
    pass


class DummyField(object):
    _translations = DummyTranslations()

    def __init__(self, data, errors=(), raw_data=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data

    def gettext(self, string):
        return self._translations.gettext(string)

    def ngettext(self, singular, plural, n):
        return self._translations.ngettext(singular, plural, n)


class ValidatorsTest(TestCase):
    """Test custom validators"""
    def setUp(self):
        self.form = DummyForm()

    def test_optional_if_field_does_not_exist(self):
        (u"Test that the field doesn't pass the optional validation when "
          "the other field doesn't exist.")
        self.assertEqual(
            OptionalIf('spam')(self.form, DummyField('eggs')),
            None
        )

    def test_optional_if_field_exists(self):
        (u'Test that the field is optional when the other field exists.')
        self.form['spam'] = DummyField(True)
        self.form['eggs'] = DummyField(None, ['Error message'])

        # When the field exists, OptionalIf should raise OptionalIf and the
        # `len()` of its `errors` attribute should be 0.
        self.assertRaises(
            StopValidation,
            OptionalIf('spam'),
            self.form,
            self.form['eggs']
        )
        self.assertEqual(len(self.form['eggs'].errors), 0)
