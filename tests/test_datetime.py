import pytest
import zoneinfo
from datetime import datetime, timezone
from database.types.utc_datetime import UTCDateTime

def test_utc_conversion():
    utc_type = UTCDateTime()
    
    # Cas 1: datetime naïf (sans fuseau horaire) -> Converti en UTC
    naive_dt = datetime(2026, 7, 7, 12, 0)
    bound_naive = utc_type.process_bind_param(naive_dt, dialect=None)
    assert bound_naive.tzinfo == timezone.utc
    
    # Cas 2: Fuseau horaire de Paris -> Converti correctement en UTC
    paris_tz = zoneinfo.ZoneInfo("Europe/Paris")
    paris_dt = datetime(2026, 7, 7, 12, 0, tzinfo=paris_tz)
    bound_paris = utc_type.process_bind_param(paris_dt, dialect=None)
    assert bound_paris.tzinfo == timezone.utc
    assert bound_paris.hour == 10  # 12h00 à Paris en été = 10h00 UTC
    
    # Cas 3: Déjà en UTC -> Aucune modification
    utc_dt = datetime(2026, 7, 7, 12, 0, tzinfo=timezone.utc)
    bound_utc = utc_type.process_bind_param(utc_dt, dialect=None)
    assert bound_utc == utc_dt