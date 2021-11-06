from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):
    def test_wait_for_db_ready(self):
        """Testing waiting for db when db is available"""
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.return_value = True
            call_command("wait_for_db")
            self.assertEqual(gi.call_count, 1)

    @patch(
        "time.sleep", return_value=True
    )  # used to override the time.sleep behavior in the "wait_for_db" command to speed up the test
    def test_wait_for_db(self, ts):
        # ts is the return value from @patch. ts needs to be passed in as an argument,
        # even if not used
        """Test waiting for db"""
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            # raise the OperationError the first 5 times that this is called,
            # the 6th call [True] will just return
            call_command("wait_for_db")
            self.assertEqual(gi.call_count, 6)
