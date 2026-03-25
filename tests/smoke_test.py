from pathlib import Path


def test_smoke_placeholder():
    assert Path('frontend/package.json').exists()
    assert Path('src/snack_store/app.py').exists()
