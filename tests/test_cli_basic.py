from typer.testing import CliRunner
from deepr.cli.main import app

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ['--help'])
    assert result.exit_code == 0
    assert 'DeepR local deep research CLI' in result.stdout
