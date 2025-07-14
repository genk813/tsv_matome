# Test Data for TMCloud

This directory contains lightweight test data for GitHub Actions and CI/CD pipelines.

## Contents

- **test_output.db** - Sample database with ~10% of production data
  - Maximum 1000 rows per table
  - All table structures and indexes preserved
  - Safe for version control (~30MB)

- **test_images/** - Sample trademark images
  - 50 randomly selected images
  - Representative of various trademark types
  - Total size: ~5-10MB

- **test_config.json** - Test configuration metadata

## Usage

### Running Tests Locally with Test Data

```bash
# Set environment variables to use test data
export TMCLOUD_DB_PATH="test_data/test_output.db"
export TMCLOUD_IMAGE_PATH="test_data/test_images"

# Run tests
pytest tests/
python comprehensive_search_test.py
```

### GitHub Actions

The CI pipeline automatically uses this test data. See `.github/workflows/test.yml`.

### Creating/Updating Test Data

```bash
# Run from project root
python scripts/create_test_data.py
```

**Warning**: This will overwrite existing test data. The script preserves production data.

## Data Sampling Strategy

- **Database**: 10% random sample, max 1000 rows per table
- **Images**: 50 random images from production set
- **Maintains referential integrity** between related tables
- **Preserves all indexes and constraints**

## Security Note

This test data is sanitized and safe for public repositories. No sensitive information is included.