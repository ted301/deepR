from deepr.config.settings import DeepRSettings

def test_config_defaults():
    s = DeepRSettings()
    assert s.model.provider == 'ollama'
    assert 'markdown' in s.output_formats
