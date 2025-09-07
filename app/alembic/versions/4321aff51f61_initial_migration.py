"""Initial migration

Revision ID: 4321aff51f61
Revises: 
Create Date: 2025-09-07 21:20:41.096899

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import Integer, String, Float, Boolean, ForeignKey

# revision identifiers, used by Alembic.
revision = '4321aff51f61'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ======== Таблицы ========
    op.create_table(
        'activities',
        sa.Column('id', Integer, primary_key=True),
        sa.Column('name', String(255), nullable=False),
        sa.Column('parent_id', Integer, sa.ForeignKey('activities.id', ondelete='SET NULL')),
        sa.UniqueConstraint('parent_id', 'name', name='uq_activities_parent_name'),
    )

    op.create_table(
        'buildings',
        sa.Column('id', Integer, primary_key=True),
        sa.Column('address', sa.Text, nullable=False),
        sa.Column('latitude', Float, nullable=False),
        sa.Column('longitude', Float, nullable=False),
    )

    op.create_table(
        'organizations',
        sa.Column('id', Integer, primary_key=True),
        sa.Column('name', String(255), nullable=False),
        sa.Column('building_id', Integer, sa.ForeignKey('buildings.id', ondelete='RESTRICT'), nullable=False),
        sa.UniqueConstraint('name', 'building_id', name='uq_organizations_name_building'),
    )

    op.create_table(
        'organization_phones',
        sa.Column('id', Integer, primary_key=True),
        sa.Column('organization_id', Integer, sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('phone', String(64), nullable=False),
        sa.Column('position', Integer, nullable=False, default=0),
        sa.Column('is_primary', Boolean, nullable=False, default=False),
        sa.UniqueConstraint('organization_id', 'phone', name='uq_org_phone_unique'),
    )

    op.create_table(
        'organization_activity',
        sa.Column('organization_id', Integer, sa.ForeignKey('organizations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('activity_id', Integer, sa.ForeignKey('activities.id', ondelete='CASCADE'), primary_key=True),
        sa.UniqueConstraint('organization_id', 'activity_id', name='uq_org_activity'),
    )

    # ======== Начальные данные (seed) ========
    activities_table = table('activities',
        column('id', Integer),
        column('name', String),
        column('parent_id', Integer),
    )

    op.bulk_insert(activities_table,
        [
            {'id': 1, 'name': 'Еда', 'parent_id': None},
            {'id': 2, 'name': 'Мясная продукция', 'parent_id': 1},
            {'id': 3, 'name': 'Молочная продукция', 'parent_id': 1},
            {'id': 4, 'name': 'Говядина', 'parent_id': 2},
            {'id': 5, 'name': 'Свинина', 'parent_id': 2},
            {'id': 6, 'name': 'Сыры', 'parent_id': 3},
            {'id': 7, 'name': 'Молоко', 'parent_id': 3},
            {'id': 8, 'name': 'Автомобили', 'parent_id': None},
            {'id': 9, 'name': 'Грузовые', 'parent_id': 8},
            {'id':10, 'name': 'Легковые', 'parent_id': 8},
            {'id':11, 'name': 'Запчасти', 'parent_id': 8},
            {'id':12, 'name': 'Аксессуары', 'parent_id': 8},
            {'id':13, 'name': 'Электроника', 'parent_id': None},
            {'id':14, 'name': 'Смартфоны', 'parent_id':13},
            {'id':15, 'name': 'Ноутбуки', 'parent_id':13},
        ]
    )

    buildings_table = table('buildings',
        column('id', Integer),
        column('address', String),
        column('latitude', Float),
        column('longitude', Float),
    )

    op.bulk_insert(buildings_table,
        [
            {'id':1, 'address':'ул. Пушкина, 10', 'latitude':55.75, 'longitude':37.61},
            {'id':2, 'address':'ул. Ленина, 5', 'latitude':59.93, 'longitude':30.33},
            {'id':3, 'address':'ул. Тверская, 12', 'latitude':55.76, 'longitude':37.62},
            {'id':4, 'address':'пр. Невский, 20', 'latitude':59.93, 'longitude':30.34},
        ]
    )

    organizations_table = table('organizations',
        column('id', Integer),
        column('name', String),
        column('building_id', Integer),
    )

    op.bulk_insert(organizations_table,
        [
            {'id':1, 'name':'TechCorp', 'building_id':1},
            {'id':2, 'name':'FoodMaster', 'building_id':2},
            {'id':3, 'name':'AutoPartsPro', 'building_id':3},
            {'id':4, 'name':'ElectroHub', 'building_id':4},
        ]
    )

    org_activity_table = table('organization_activity',
        column('organization_id', Integer),
        column('activity_id', Integer),
    )

    op.bulk_insert(org_activity_table,
        [
            {'organization_id':1, 'activity_id':14},
            {'organization_id':1, 'activity_id':15},
            {'organization_id':2, 'activity_id':1},
            {'organization_id':2, 'activity_id':2},
            {'organization_id':2, 'activity_id':3},
            {'organization_id':2, 'activity_id':4},
            {'organization_id':2, 'activity_id':5},
            {'organization_id':2, 'activity_id':6},
            {'organization_id':2, 'activity_id':7},
            {'organization_id':3, 'activity_id':8},
            {'organization_id':3, 'activity_id':9},
            {'organization_id':3, 'activity_id':10},
            {'organization_id':3, 'activity_id':11},
            {'organization_id':3, 'activity_id':12},
            {'organization_id':4, 'activity_id':13},
            {'organization_id':4, 'activity_id':14},
            {'organization_id':4, 'activity_id':15},
        ]
    )

    phones_table = table('organization_phones',
        column('id', Integer),
        column('organization_id', Integer),
        column('phone', String),
        column('position', Integer),
        column('is_primary', Boolean),
    )

    op.bulk_insert(phones_table,
        [
            {'id':1, 'organization_id':1, 'phone':'+7-999-111-22-33', 'position':0, 'is_primary':True},
            {'id':2, 'organization_id':1, 'phone':'+7-999-111-22-34', 'position':1, 'is_primary':False},
            {'id':3, 'organization_id':2, 'phone':'+7-888-222-33-44', 'position':0, 'is_primary':True},
            {'id':4, 'organization_id':2, 'phone':'+7-888-222-33-45', 'position':1, 'is_primary':False},
            {'id':5, 'organization_id':3, 'phone':'+7-777-333-44-55', 'position':0, 'is_primary':True},
            {'id':6, 'organization_id':4, 'phone':'+7-666-444-55-66', 'position':0, 'is_primary':True},
            {'id':7, 'organization_id':4, 'phone':'+7-666-444-55-67', 'position':1, 'is_primary':False},
            {'id':8, 'organization_id':4, 'phone':'+7-666-444-55-68', 'position':2, 'is_primary':False},
        ]
    )


def downgrade():
    op.drop_table('organization_activity')
    op.drop_table('organization_phones')
    op.drop_table('organizations')
    op.drop_table('activities')
    op.drop_table('buildings')
