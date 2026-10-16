#!/usr/bin/env bash
# Re-apply US localization (USD, US dates, US wording) across the codebase.
# Idempotent: safe to run again after merging upstream changes.
#   bash scripts/us_localize.sh && git diff --stat
set -euo pipefail
cd "$(dirname "$0")/.."

# Tracked source files, excluding migrations and this script.
files() { git ls-files -- "$@" | grep -v '/migrations/' | grep -v '^scripts/us_localize.sh$' || true; }
sedi() { local expr=("$@"); while IFS= read -r f; do [ -n "$f" ] && sed -i -E "${expr[@]}" "$f"; done; }

# --- Currency ---------------------------------------------------------------
files '*.html' '*.py' '*.js' '*.txt' | sedi -e 's/£/$/g'
files '*.py' | sedi -e "s/currency=(['\"])gbp\1/currency=\1usd\1/g" \
                    -e "s/(['\"])currency\1: (['\"])gbp\2/\1currency\1: \2usd\2/g" \
                    -e 's/amount_gbp/amount_paid_usd/g'

# --- Template date filters -> US order ----------------------------------------
files '*.html' '*.txt' | sedi \
  -e "s/date:([\"'])l, d F Y\1/date:\1l, F j, Y\1/g" \
  -e "s/date:([\"'])l d F Y\1/date:\1l, F j, Y\1/g" \
  -e "s/date:([\"'])l d M Y\1/date:\1l, M j, Y\1/g" \
  -e "s/date:([\"'])D d M Y\1/date:\1D, M j, Y\1/g" \
  -e "s/date:([\"'])d M Y H:i\1/date:\1M j, Y g:i A\1/g" \
  -e "s/date:([\"'])j M Y, H:i\1/date:\1M j, Y, g:i A\1/g" \
  -e "s/date:([\"'])d M Y\1/date:\1M j, Y\1/g" \
  -e "s/date:([\"'])j M Y\1/date:\1M j, Y\1/g" \
  -e "s/date:([\"'])D d M\1/date:\1D, M j\1/g" \
  -e "s/date:([\"'])d M\1/date:\1M j\1/g" \
  -e "s/date:([\"'])j M\1/date:\1M j\1/g"

# --- Python display formats -> US order ---------------------------------------
files '*.py' | sedi \
  -e 's/%A %-d %B %Y/%A, %B %-d, %Y/g' \
  -e 's/%d %B %Y at %H:%M/%B %d, %Y at %I:%M %p/g' \
  -e 's/%-d %b %Y/%b %-d, %Y/g' \
  -e 's/%d %b %Y/%b %d, %Y/g' \
  -e "s/'date_of_birth': '01 May 2012'/'date_of_birth': 'May 1, 2012'/g" \
  -e "s/strftime\\('%d %b'\\)/strftime('%b %d')/g"

# --- Date parsing: day-first -> month-first (2-digit years stay rejected) -------
files '*.py' | sedi -e "s#'%d/%m/%Y'#'%m/%d/%Y'#g" -e "s#'%d-%m-%Y'#'%m-%d-%Y'#g" \
                    -e 's#DD/MM/YYYY, DD-MM-YYYY#MM/DD/YYYY, MM-DD-YYYY#g'
files '*.html' | sedi -e 's#YYYY-MM-DD or DD/MM/YYYY#YYYY-MM-DD or MM/DD/YYYY#g'

# --- Locale and time zone -----------------------------------------------------
sed -i -E -e "s/^LANGUAGE_CODE = 'en-gb'/LANGUAGE_CODE = 'en-us'/" \
          -e "s#^TIME_ZONE = 'Europe/London'#TIME_ZONE = os.environ.get('TIME_ZONE', 'America/Denver')#" \
          dojo/settings.py

# --- Visible UI wording (labels and messages only; identifiers untouched) ------
files '*.html' | sedi \
  -e 's/>Town \/ City</>City</g' \
  -e 's/>County</>State</g' \
  -e 's/>Postcode</>ZIP code</g' \
  -e 's/Organisation name/Organization name/g' \
  -e 's/(>|"| )Organisation(<| |")/\1Organization\2/g' \
  -e 's/(your|the|this|an|Create|Create your|No) organisation/\1 organization/g' \
  -e 's/Your organisations/Your organizations/g' \
  -e 's/>Colour</>Color</g' \
  -e "s/(theme|Custom|club's|Your|Header|Calendar|Save|button|club’s) colour/\\1 color/g" \
  -e 's/Licence (no\.|number|expiry)/License \1/g' \
  -e 's/([Cc])oaching licence/\1oaching license/g' \
  -e 's/(>| )DBS(<| )/\1Background check\2/g' \
  -e 's/DBS (number|expiry|or)/Background check \1/g' \
  -e 's/>Enrol</>Enroll</g' \
  -e 's/and licence tracking/and license tracking/g' \
  -e 's/such as cards and Bacs Direct Debit/such as cards and US bank accounts (ACH)/g' \
  -e 's/Direct Debits take about 3 working days to clear/Bank payments take a few business days to clear/g'
files '*.py' | sedi \
  -e "s/'Organisation name is required\.'/'Organization name is required.'/g" \
  -e 's/(member|members|part) of this organisation/\1 of this organization/g' \
  -e "s/valid colour/valid color/g" \
  -e "s/header colour should/header color should/g" \
  -e "s/Calendar colour updated/Calendar color updated/g" \
  -e "s/'BACS transfer'/'Bank transfer (ACH)'/g"

echo "US localization applied."
