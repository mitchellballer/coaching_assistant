from flaskr.db import get_db
import datetime


def most_recent_activity(athlete_id):
    db = get_db()
    most_recent = db.execute(
        'SELECT max(start_date) FROM activity WHERE athlete_id = ?',
        (athlete_id,)).fetchone()[0]
    if most_recent:
        epoch = datetime.strptime(most_recent, "%Y-%m-%d %H:%M:%S").timestamp()
        return int(epoch)
    else:
        return None
