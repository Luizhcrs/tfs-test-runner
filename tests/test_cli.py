"""Smoke tests for the multi-command CLI (Click group)."""
from pathlib import Path
from click.testing import CliRunner
from tfs_test_runner.cli import cli


def test_cli_top_help_shows_subcommands():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    for sub in ("plan", "validate", "init", "screenshots"):
        assert sub in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "tfs-test-runner" in result.output


def test_cli_plan_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["plan", "--help"])
    assert result.exit_code == 0
    assert "INPUT_XLSX" in result.output
    assert "--llm" in result.output
    assert "--argos" in result.output
    assert "--phases" in result.output


def test_cli_validate_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "--help"])
    assert result.exit_code == 0
    assert "--strict" in result.output


def test_cli_init_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "--help"])
    assert result.exit_code == 0
    assert "--with-sample" in result.output


def test_cli_validate_runs_on_sample(tmp_path: Path):
    runner = CliRunner()
    sample = Path(__file__).parent.parent / "examples" / "sample.xlsx"
    if not sample.exists():
        # Generate on the fly so the test doesn't depend on a prior run
        from examples.generate_sample import main as gen
        gen()
    result = runner.invoke(cli, ["validate", str(sample)])
    assert result.exit_code == 0
    assert "Test cases" in result.output
    assert "Total steps" in result.output


def test_cli_plan_runs_on_sample(tmp_path: Path):
    runner = CliRunner()
    sample = Path(__file__).parent.parent / "examples" / "sample.xlsx"
    out = tmp_path / "plan.html"
    result = runner.invoke(cli, ["plan", str(sample), "-o", str(out)])
    assert result.exit_code == 0, result.output
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "<!doctype html>" in html


def test_cli_plan_force_required(tmp_path: Path):
    runner = CliRunner()
    sample = Path(__file__).parent.parent / "examples" / "sample.xlsx"
    out = tmp_path / "plan.html"
    out.write_text("existing", encoding="utf-8")
    result = runner.invoke(cli, ["plan", str(sample), "-o", str(out)])
    assert result.exit_code == 1
    assert "already exists" in result.output


def test_cli_plan_llm_argos_mutually_exclusive(tmp_path: Path):
    runner = CliRunner()
    sample = Path(__file__).parent.parent / "examples" / "sample.xlsx"
    out = tmp_path / "plan.html"
    result = runner.invoke(cli, ["plan", str(sample), "-o", str(out), "-f", "--llm", "--argos"])
    assert result.exit_code == 2
    assert "mutually exclusive" in result.output


def test_cli_init_creates_files(tmp_path: Path):
    runner = CliRunner()
    target = tmp_path / "qa-plan"
    result = runner.invoke(cli, ["init", str(target)])
    assert result.exit_code == 0
    assert (target / "cases.xlsx").exists()
    assert (target / "phases.yaml").exists()
    assert (target / "glossary.yaml").exists()
    assert (target / "README.md").exists()
