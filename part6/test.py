"""Run with python -B -m unittest discover -s part6 -p test.py -v.

Set MARS_JAR and optionally JAVA to execute the generated assembly in MARS.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from compiler import compile_source


class CompilerTests(unittest.TestCase):
    def test_historical_fixtures(self):
        for path in sorted(Path(__file__).with_name("test").glob("*.ml")):
            with self.subTest(path=path.name):
                if path.name in ("test.5.1.ml", "test.5.2.ml"):
                    with self.assertRaises(ValueError):
                        compile_source(path.read_text())
                else:
                    self.assertIn(".text", compile_source(path.read_text()))

    def test_diagnostics_and_recovery(self):
        invalid = [
            "", "begin", "begin int x end", "begin write(1);",
            "begin end write(1);", "begin if (True) { write(1); end",
            "begin if (1) { write(1); } end",
            "begin while (1) { write(1); } end",
            "begin x := 1; end", "begin write(x + 1); end",
            "begin int x; int x; end", "begin int x; x := True; end",
            "begin bool x; x := 1; end", 'begin string x; x := False; end',
            "begin write(-True); end", "begin write(not 1); end",
            "begin bool b; read(b); end", "begin string s; read(s); end",
            "begin write(2147483648); end", "begin write(-2147483649); end",
            'begin write("unterminated); end', 'begin write("\\q"); end',
            "begin write(@); end", "begin write(); end",
        ]
        expected = compile_source("begin write(7); end")
        for source in invalid:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    compile_source(source)
                self.assertEqual(expected, compile_source("begin write(7); end"))
        with self.assertRaisesRegex(ValueError, "line 3"):
            compile_source("begin\nint x;\nx := ;\nend")

    def test_long_statement_list_and_blank_lines(self):
        source = "\n" * 1100 + "begin\n" + "\n".join(
            f"int x{i};" for i in range(1100)
        ) + "\nend"
        self.assertIn("user_x1099:", compile_source(source))
        with self.assertRaisesRegex(ValueError, "50,000"):
            compile_source(" " * 50001)
        with self.assertRaisesRegex(ValueError, "too deep"):
            compile_source("begin write(" + "(" * 1100 + "1" + ")" * 1100 + "); end")

    def test_cli_failure_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "input.ml", Path(directory) / "out.asm"
            source.write_text("begin int x end")
            output.write_text("previous output")
            result = subprocess.run(
                [sys.executable, "-B", str(Path(__file__).with_name("compiler.py")),
                 str(source), str(output)], capture_output=True, text=True, timeout=10,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Parse error", result.stderr)
            self.assertEqual("previous output", output.read_text())


@unittest.skipUnless(os.environ.get("MARS_JAR"), "Set MARS_JAR for real assembly execution")
class ExecutionTests(unittest.TestCase):
    def run_source(self, source, expected, inputs=""):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.asm"
            output.write_text(compile_source(source), encoding="utf-8")
            result = subprocess.run([
                os.environ.get("JAVA", "java"),
                "-Djava.util.prefs.userRoot=" + directory,
                "-jar", os.environ["MARS_JAR"], "nc", "sm", "me", "ae1", "se1",
                "100000", str(output),
            ], input=inputs, capture_output=True, text=True, timeout=20)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertNotIn("maximum step limit", result.stderr.lower())
            self.assertEqual(expected, result.stdout, result.stderr)

    def test_historical_execution(self):
        cases = {
            "1.1": "", "1.2": "\nTrue", "1.3": "\nFalse", "1.4": "\nTrue",
            "1.5": "\nFalse", "2.1": "\nTrue\nTrue\nTrue\nFalse",
            "2.2": "\nTrue\nFalse\nFalse\nFalse", "2.3": "\nFalse\nTrue",
            "2.4": "\nTrue\nTrue", "2.5": "\nTrue", "2.6": "\nTrue",
            "3.1": "\nTrue\nFalse\nFalse", "3.2": "\nTrue\nTrue\nFalse",
            "3.3": "\nFalse\nFalse\nTrue", "3.4": "\nFalse\nTrue\nTrue",
            "3.5": "\nTrue\nFalse", "3.6": "\nFalse\nTrue",
            "6.1": "\nYes\n\nDone\n", "6.2": "\nDone\n",
            "6.3": "\nYes\n", "6.4": "\nNo\n", "6.5": "\nYes\n",
            "6.6": "\n25\n\nDone\n", "7.1": "\n10\n24\n", "7.2": "\n5 \n3 \n1 ",
            "8.1": "".join(f"\n{i} {j} \n" for i in range(5) for j in range(5)
                          if (i + j) % 3 == 0 and (i % 2 == 0 or j % 2 == 0)),
            "8.1.1": "".join(
                f"\nstarting while loop {i}" +
                "".join(f"\n{i}, {j}" for j in range(1, 6)) +
                f"\ni is equal to {i + 1}" for i in range(5)),
            "8.2": "\nHere\n",
        }
        for case, expected in cases.items():
            with self.subTest(case=case):
                source = Path(__file__).with_name("test") / f"test.{case}.ml"
                self.run_source(source.read_text(), expected, "5\n")

    def test_negation_and_boolean_aliases(self):
        self.run_source("""
            begin bool ready; ready := True;
            write(not ready, " ", !ready, " ", not (1 < 2));
            write(False || True && False, " ", True && !False);
            end
        """, "\nFalse False False\nFalse True")

    def test_nested_and_sequential_branches(self):
        self.run_source("""
            begin
            if (True) { if (False) { write("bad"); } else { write("A"); } }
            else { write("bad"); }
            if (False) { write("bad"); } else {
                if (True) { write("B"); } else { write("bad"); }
            }
            if (False) { write("bad"); }
            write("C");
            end
        """, "\nA\nB\nC")

    def test_arithmetic_and_32_bit_literals(self):
        self.run_source("""
            begin int x; x := 3;
            write(2 + 3 * 4, " ", (2 + 3) * 4, " ", 20 / 3, " ", 20 % 3);
            write(20 - 3 - 2, " ", 24 / 3 / 2, " ", -x);
            write(-2147483648, " ", 2147483647, " ", 0002, " ", -0002);
            end
        """, "\n14 20 6 2\n15 4 -3\n-2147483648 2147483647 2 -2")

    def test_strings_and_identifier_collisions(self):
        self.run_source(r'''
            begin int temp0; int temp1; int bool0; int mips1; int main; int _x;
            read(temp0, temp1);
            bool0 := temp0 + temp1; mips1 := 1; main := 2; _x := 3;
            string x; string y;
            x := "x"; y := x;
            write(y, " ", "True", " ", "False", " ", "7", " ", 7);
            write("a|~ b\"c\\d\n", bool0, " ", mips1 + main + _x);
            end
        ''', '\nx True False 7 7\na|~ b"c\\d\n9 6', "4\n5\n")


if __name__ == "__main__":
    unittest.main()
