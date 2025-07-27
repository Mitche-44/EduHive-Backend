from app import create_app
from extensions import db
from models.badge import Badge

app = create_app()

with app.app_context():
    # Drop and recreate only the badges table
    Badge.__table__.drop(db.engine, checkfirst=True)
    db.create_all()

    # Define all badge instances
    badge1 = Badge(
        title="Software Engineering",
        awarded=3,
        winners="Jane Wambui, Mitchelle Ngetich, Grace Zawadi",
        image_url="https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F304806%2F59cce1ab07a24566ba2d600e75fbf142%2FAward%20Image-20.svg?generation=1726517815415410&alt=media"
    )

    badge2 = Badge(
        title="Python Coder",
        awarded=2,
        winners="Eric Mongare, Kennedy Odero",
        image_url="https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F1488634%2F09e1f99bdf3222934ad7769409ec3f6d%2FBadge-26.svg?generation=1727468059623106&alt=media"
    )

    badge3 = Badge(
        title="Cyber Security",
        awarded=1,
        winners="Arnold Wainaina",
        image_url="https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F304806%2F2904e2b1e8acbde8d5ad13443579dfda%2FAward%20Image-18.svg?generation=1726517780511342&alt=media"
    )

    badge4 = Badge(
        title="Machine Learning",
        awarded=4,
        winners="Dennis Wachira, Natasha Onsongo, Enock Korir, Masela Ogendo",
        image_url="https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F1488634%2F3baaa158e1ff014b90edc64b110f69bb%2FAward%20Image.svg?generation=1727276946467793&alt=media"
    )

    badge5 = Badge(
        title="UI Design",
        awarded=1,
        winners="Christine",
        image_url="https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F304806%2F21f090fa8230bc1b9c04277ab18e00f5%2FAward%20Image.svg?generation=1727209916661102&alt=media"
    )

    badge6 = Badge(
        title="UX Design",
        awarded=2,
        winners="Fancy Byegon, Alex Kotut",
        image_url="https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F304806%2Fb4f4e39130efa963a447e045350fd6bf%2FAward%20Image-10.svg?generation=1726113967704528&alt=media"
    )

    badge7 = Badge(
        title="Graphic Design",
        awarded=2,
        winners="Celestine Mecheo, Joy Malinda",
        image_url="https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F304806%2Fb4f4e39130efa963a447e045350fd6bf%2FAward%20Image-10.svg?generation=1726113967704528&alt=media"
    )

    badge8 = Badge(
        title="Best Contributor",
        awarded=4,
        winners="Hope Wasonga, Munga Michael, Darwin Osingo, Arnold Kulavi",
        image_url="https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F304806%2F5ef10fe7ebd4bd327af4a5ceaac8cf35%2FAward%20Image-23.svg?generation=1726517891877959&alt=media"
    )

    db.session.add_all([badge1, badge2, badge3, badge4, badge5, badge6, badge7, badge8])
    db.session.commit()
    print("Added badges successfully!")
