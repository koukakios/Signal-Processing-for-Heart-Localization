import unittest
from unittest.mock import patch
from src.module_2.CommandProcessor import CommandProcessor

class TestCommands(unittest.TestCase):
    def setUp(self):
        self.BPM = 100
        self.cmd = CommandProcessor()
        self.cmd.register_command("help", self.cmd.print_help, helpmsg="Show this help menu")
        general_group = self.cmd.register_symbolic_group("General", "Contains specs and props for general purposes")
        self.cmd.register_symbolic_spec("G", general_group, lambda: self, "General things")
        self.cmd.register_symbolic_prop("BPM", general_group, lambda obj: obj.BPM, lambda obj, val: setattr(obj, "BPM", val), dtype=int, helpmsg="The BPM of the heart signal")
        
    def test_set_bpm(self):
        self.cmd.process_command("G BPM 50")
        self.assertEqual(self.BPM, 50)
        
    def test_print_help(self):
        expected = [
            "\nCommands:",
            "  exit                            Shutdown the application",
            "  help                            Show this help menu",
            "\nSymbolic groups:",
            "  General         Contains specs and props for general purposes",
            "\nSymbolic parameters:",
            "  Usage:",
            "    <specifier> <prop> <value> to set specifier.prop to value",
            "    <specifier> <prop>         to print specifier.prop\n",
            "  General",
            "    Specifiers:",
            "      G          General things",
            "    Props:",
            "      BPM        <int>    The BPM of the heart signal",
        ]
        with patch("builtins.print") as mock_print:
            self.cmd.process_command("help")
            actual = [call.args[0] for call in mock_print.call_args_list]
        self.assertEqual(actual, expected)