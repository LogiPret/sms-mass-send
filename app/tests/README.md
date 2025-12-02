# Test Files for SMS Mass Send

These test files cover various CSV formats and edge cases.

## Test Files

| File | Description |
|------|-------------|
| `test_standard.csv` | Basic CSV with standard columns |
| `test_multiphone.csv` | Multi-phone format: `work \| 514... : mobile \| 438...` |
| `test_semicolon.csv` | French/European CSV with `;` separator |
| `test_tab.tsv` | Tab-separated values |
| `test_velocity_crm.csv` | Simulates Velocity CRM export format |
| `test_edge_cases.csv` | Special characters, missing data, quotes |
| `test_phone_formats.csv` | Various phone number formats |

## Test Phone Numbers

All files use these 2 test numbers:
- `+14389266456` (438-926-6456)
- `+15798819696` (579-881-9696)

## Expected Behavior

### Multi-phone Priority
1. **Mobile/Cell/Cellulaire** (highest)
2. **Work/Travail/Bureau**
3. **Home/Maison/Domicile**
4. **First found** (fallback)

### Contacts to Skip
- Missing first name (prénom vide)
- Invalid phone (< 10 digits)

### Debug Mode
Set `DEBUG_MODE = true` in script.js to see parsing results without sending.
