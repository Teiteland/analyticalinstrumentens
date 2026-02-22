# Instrumentoversikt GUI

Et Python GUI-program for å administrere instrumenter, kolonner og vedlikeholdslogg.

## Krav

- Python 3.x
- customtkinter

## Installering

```bash
pip install -r requirements.txt
```

## Kjøring

```bash
python main.py
```

```
Du kan aktivere venv og kjøre slik:
source .venv/bin/activate
python main.py
Eller kjør direkte med:
.venv/bin/python main.py
```

## Funksjonalitet

- **Dashboard** - Oversikt over instrumenter og statistikk
- **Instrumenter** - Legg til, rediger og slett instrumenter
- **Kolonner** - Administonner per instrument
- **Vedrer kollikehold** - Loggfør vedlikeholdshendelser
- **Søk og filtrering** - Finn instrumenter etter type

## Databaseskjema

### instruments
| Kolonne | Type | Beskrivelse |
|---------|------|-------------|
| id | INTEGER | Primærnøkkel |
| name | TEXT | Navn |
| type | TEXT | Type |
| model | TEXT | Modell |
| manufacturer | TEXT | Produsent |
| serial_number | TEXT | Serienummer |
| purchase_date | TEXT | Kjøpsdato |
| notes | TEXT | Notater |
| status | TEXT | Status (standard: Active) |
| created_at | TEXT | Opprettet |

### columns
| Kolonne | Type | Beskrivelse |
|---------|------|-------------|
| id | INTEGER | Primærnøkkel |
| instrument_id | INTEGER | Fremmednøkkel til instruments |
| name | TEXT | Navn |
| column_type | TEXT | Kolonnetyp |
| length_cm | REAL | Lengde (cm) |
| diameter_mm | REAL | Diameter (mm) |
| pore_size | TEXT | Porestørrelse |
| install_date | TEXT | Installasjonsdato |
| status | TEXT | Status |
| notes | TEXT | Notater |
| created_at | TEXT | Opprettet |

### maintenance
| Kolonne | Type | Beskrivelse |
|---------|------|-------------|
| id | INTEGER | Primærnøkkel |
| instrument_id | INTEGER | Fremmednøkkel til instruments |
| date | TEXT | Dato |
| maintenance_type | TEXT | Vedlikeholdstype |
| description | TEXT | Beskrivelse |
| performed_by | TEXT | Utført av |
| cost | REAL | Kostnad |
| created_at | TEXT | Opprettet |
