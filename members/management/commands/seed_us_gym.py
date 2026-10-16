"""
Seed a big, fictional US taekwondo school for load and demo testing:
Glacier Peak Taekwondo, Kalispell MT.

    python manage.py seed_us_gym                  # 300 students
    python manage.py seed_us_gym --members 800    # bigger
    python manage.py seed_us_gym --reset          # delete this gym first, then reseed

Everything is made up. Emails use example.com and phone numbers use the
fictional 555-01xx range, so nothing can reach a real person.
"""

import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

SLUG = 'glacier-peak-taekwondo'
PASSWORD = 'demo1234'

FIRST_KIDS = [
    'Liam', 'Olivia', 'Noah', 'Emma', 'Oliver', 'Ava', 'Elijah', 'Sophia', 'James', 'Isabella',
    'William', 'Mia', 'Benjamin', 'Evelyn', 'Lucas', 'Harper', 'Henry', 'Luna', 'Theodore', 'Camila',
    'Jack', 'Gianna', 'Levi', 'Elizabeth', 'Alexander', 'Eleanor', 'Jackson', 'Ella', 'Mateo', 'Abigail',
    'Daniel', 'Sofia', 'Michael', 'Avery', 'Mason', 'Scarlett', 'Sebastian', 'Emily', 'Ethan', 'Aria',
    'Logan', 'Penelope', 'Owen', 'Chloe', 'Samuel', 'Layla', 'Jacob', 'Mila', 'Asher', 'Nora',
    'Aiden', 'Hazel', 'John', 'Madison', 'Joseph', 'Ellie', 'Wyatt', 'Lily', 'David', 'Nova',
    'Leo', 'Isla', 'Luke', 'Grace', 'Julian', 'Violet', 'Hudson', 'Aurora', 'Grayson', 'Riley',
    'Matthew', 'Zoey', 'Ezra', 'Willow', 'Gabriel', 'Emilia', 'Carter', 'Stella', 'Isaac', 'Zoe',
    'Jayden', 'Victoria', 'Luca', 'Hannah', 'Anthony', 'Addison', 'Dylan', 'Leah', 'Lincoln', 'Lucy',
    'Thomas', 'Eliana', 'Maverick', 'Ivy', 'Elias', 'Everly', 'Josiah', 'Lillian', 'Charles', 'Paisley',
    'Kai', 'Wren', 'Beckett', 'Juniper', 'Colt', 'Sage', 'Rhett', 'Hadley', 'Tucker', 'Kinsley',
]
FIRST_ADULTS = [
    'Michael', 'Jennifer', 'David', 'Jessica', 'Chris', 'Sarah', 'Matt', 'Ashley', 'Josh', 'Amanda',
    'Ryan', 'Stephanie', 'Andrew', 'Nicole', 'Justin', 'Megan', 'Brandon', 'Rachel', 'Tyler', 'Lauren',
    'Kevin', 'Heather', 'Jason', 'Amber', 'Eric', 'Melissa', 'Aaron', 'Kayla', 'Adam', 'Brittany',
    'Travis', 'Danielle', 'Cody', 'Tiffany', 'Dustin', 'Erin', 'Kyle', 'Courtney', 'Derek', 'Kelsey',
    'Shane', 'Lindsey', 'Brent', 'Jenna', 'Wade', 'Tara', 'Clint', 'Shelby', 'Garrett', 'Molly',
]
LAST = [
    'Anderson', 'Johnson', 'Miller', 'Olson', 'Peterson', 'Larson', 'Nelson', 'Hansen', 'Erickson',
    'Smith', 'Brown', 'Davis', 'Wilson', 'Moore', 'Taylor', 'Thomas', 'Jackson', 'White', 'Harris',
    'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee',
    'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King', 'Wright', 'Lopez', 'Hill', 'Scott',
    'Green', 'Adams', 'Baker', 'Gonzalez', 'Carter', 'Mitchell', 'Perez', 'Roberts', 'Turner',
    'Phillips', 'Campbell', 'Parker', 'Evans', 'Edwards', 'Collins', 'Stewart', 'Morris', 'Murphy',
    'Cook', 'Rogers', 'Morgan', 'Cooper', 'Peterson', 'Bailey', 'Reed', 'Kelly', 'Howard', 'Cox',
    'Ward', 'Richardson', 'Watson', 'Brooks', 'Wood', 'James', 'Bennett', 'Gray', 'Hughes', 'Price',
    'Sanders', 'Myers', 'Long', 'Ross', 'Foster', 'Jensen', 'Lindgren', 'Bergstrom', 'Swanson',
    'Running Crane', 'Old Person', 'Kipp', 'Yellow Owl', 'Nguyen', 'Kim', 'Patel', 'Schmidt', 'Weber',
]
STREETS = [
    'Main St', '1st Ave W', '2nd Ave E', '3rd St W', '4th Ave N', 'Meridian Rd', 'Whitefish Stage',
    'Willow Glen Dr', 'Two Mile Dr', 'Three Mile Dr', 'Four Mile Dr', 'Foys Lake Rd', 'Airport Rd',
    'Reserve Dr', 'Conrad Dr', 'Grandview Dr', 'Sunset Blvd', 'Woodland Ave', 'Northridge Dr',
    'Buffalo Hill Dr', 'Lawrence Park Rd', 'Hwy 2 E', 'Hwy 93 S', 'Helena Flats Rd', 'Church Dr',
]
TOWNS = [('Kalispell', '59901'), ('Kalispell', '59901'), ('Kalispell', '59901'), ('Whitefish', '59937'),
         ('Columbia Falls', '59912'), ('Bigfork', '59911'), ('Somers', '59932'), ('Evergreen', '59901')]
MEDICAL = [
    'Asthma. Inhaler in gear bag; let them sit out if breathless.',
    'Peanut allergy (severe). EpiPen in front desk drawer.',
    'Type 1 diabetes. Manages own levels; glucose tabs in bag.',
    'ADHD. Does best with clear, short instructions and a front-row spot.',
    'Wears glasses. Remove for sparring.',
    'Past concussion (2025). Cleared by doctor; no head contact for 6 months.',
    'Mild hearing loss in left ear. Stand on their right when instructing.',
    'Bee sting allergy. EpiPen in parent\'s car.',
    'Previous ACL repair, right knee. Avoid jumping kicks until cleared.',
    'High blood pressure, medicated. Watch for over-exertion.',
    'Epilepsy, well controlled. No known triggers; parent has seizure plan on file.',
    'Lower back injury. Modify forward stances; no bridging.',
]
NOTES = [
    'Ready for belt test next cycle.',
    'Needs work on forms (poomsae) before testing.',
    'Great attitude, helps newer students.',
    'Parent asked about the competition team.',
    'Missed several classes in a row; follow up with family.',
    'Interested in private lessons.',
    'Moving up to the advanced class next month.',
    'Uniform too small; parent ordering a new one.',
    'Strong sparring, needs focus on self-control.',
    'Asked about leadership/assistant instructor program.',
]

# (name, color, order). Order is also roughly how long it takes to get there.
BELTS = [
    ('White', '#ffffff'), ('Sr. White', '#f3f4f6'), ('Yellow', '#facc15'), ('Sr. Yellow', '#eab308'),
    ('Green', '#22c55e'), ('Sr. Green', '#15803d'), ('Blue', '#3b82f6'), ('Sr. Blue', '#1d4ed8'),
    ('Red', '#ef4444'), ('Sr. Red', '#b91c1c'), ('Black Stripe', '#3f3f46'),
    ('1st Dan', '#111111'), ('2nd Dan', '#111111'), ('3rd Dan', '#111111'),
]

# (name, schedule, capacity, age range, belt index range, coaches)
CLASSES = [
    ('Little Dragons (4–6)', [(0, '16:30', '17:05'), (2, '16:30', '17:05')], 20, (4, 6), (0, 4), ['jordan']),
    ('Little Dragons (4–6) T/Th', [(1, '16:30', '17:05'), (3, '16:30', '17:05')], 20, (4, 6), (0, 4), ['jordan']),
    ('Juniors: White – Sr. Yellow', [(0, '17:10', '18:00'), (2, '17:10', '18:00')], 30, (7, 12), (0, 3), ['jordan', 'casey']),
    ('Juniors: Green – Sr. Blue', [(1, '17:10', '18:00'), (3, '17:10', '18:00')], 30, (7, 13), (4, 7), ['casey']),
    ('Juniors: Red – Black', [(1, '18:05', '18:55'), (3, '18:05', '18:55')], 25, (9, 15), (8, 12), ['casey', 'owner']),
    ('Teens & Adults', [(0, '18:45', '19:45'), (2, '18:45', '19:45')], 35, (13, 75), (0, 13), ['owner', 'sam']),
    ('Teens & Adults: Advanced', [(1, '19:00', '20:00'), (3, '19:00', '20:00')], 25, (13, 75), (6, 13), ['owner']),
    ('Black Belt Club', [(4, '16:00', '17:00')], 25, (8, 75), (10, 13), ['owner']),
    ('Competition Team', [(5, '09:00', '11:00')], 20, (8, 40), (4, 13), ['owner', 'casey']),
    ('Fall Self-Defense (Krav)', [(4, '19:00', '20:30')], 24, (12, 75), (0, 13), ['sam']),
]


def phone(n):
    return f'(406) 555-01{n % 100:02d}'


def chance(p):
    return random.random() < p


class Command(BaseCommand):
    help = 'Seed a large fictional US taekwondo school (Glacier Peak Taekwondo) for testing'

    def add_arguments(self, parser):
        parser.add_argument('--members', type=int, default=300, help='Active students to create (default 300)')
        parser.add_argument('--weeks', type=int, default=26, help='Weeks of attendance history (default 26)')
        parser.add_argument('--reset', action='store_true', help='Delete this gym (and only this gym) first')
        parser.add_argument('--seed', type=int, default=406, help='Random seed, for repeatable data')

    def handle(self, *args, **opts):
        from organisations.models import Organisation
        random.seed(opts['seed'])
        self.today = date.today()

        if Organisation.objects.filter(slug=SLUG).exists():
            if not opts['reset']:
                self.stderr.write(f'{SLUG} already exists. Run again with --reset to rebuild it.')
                return
            self._reset()

        with transaction.atomic():
            org = self._org()
            staff = self._staff(org)
            stages = self._belts(org)
            policies = self._billing(org)
            fields = self._custom_fields(org)
            classes = self._classes(org, staff)
            members = self._members(org, opts['members'], stages, classes, policies, fields, staff)
            self._attendance(classes, opts['weeks'])
            self._invoices(org, members)
            self._gradings(org, stages, members)
            self._former_members(org, max(10, opts['members'] // 10))
            self._applications(org)
            self._announcements(org, staff)

        self.stdout.write(self.style.SUCCESS(f'\nDone: {org.name}'))
        self.stdout.write(f'  Log in at /login/ as owner / {PASSWORD} (admin) or casey / {PASSWORD} (coach)')
        self.stdout.write(f'  Dashboard: /org/{SLUG}/')

    def _say(self, text):
        self.stdout.write(f'  {text}')

    # ── Reset ────────────────────────────────────────────────────────────────

    def _reset(self):
        from organisations.models import Organisation, OrganisationMember
        from progression.models import Grading
        org = Organisation.objects.get(slug=SLUG)
        user_ids = list(OrganisationMember.objects.filter(organisation=org).values_list('user_id', flat=True))
        with transaction.atomic():
            Grading.objects.filter(organisation=org).delete()  # gradings protect their belt system
            org.delete()  # cascades to members, classes, invoices...
        User.objects.filter(pk__in=user_ids, is_superuser=False, organisation_memberships__isnull=True).delete()
        self._say(f'Deleted existing {SLUG}')

    # ── Gym, staff, belts, billing ───────────────────────────────────────────

    def _org(self):
        from organisations.features import FEATURES_BY_KEY
        from organisations.models import Organisation
        from organisations.optional_fields import OPTIONAL_FIELDS_BY_KEY
        org = Organisation.objects.create(
            slug=SLUG,
            name='Glacier Peak Taekwondo',
            email='frontdesk@glacierpeak-tkd.example.com',
            phone='(406) 555-0100',
            website='https://glacierpeak-tkd.example.com',
            features={key: True for key in FEATURES_BY_KEY},
            optional_fields={key: True for key in OPTIONAL_FIELDS_BY_KEY},
            settings={
                'sidebar_color': '#14324a', 'sidebar_color_dark': '#0e2536',
                'accent_color': '#c2410c', 'accent_hover': '#9a3412',
                'two_factor': Organisation.TWO_FACTOR_OPTIONAL,
                'demo': True,
            },
        )
        self._say(f'Gym: {org.name}')
        return org

    def _staff(self, org):
        from organisations.models import OrganisationMember
        people = [
            ('owner', 'Dana', 'Whitfield', 'org_admin', 'Owner & head instructor, 4th Dan'),
            ('casey', 'Casey', 'Lindgren', 'coach', '3rd Dan'),
            ('jordan', 'Jordan', 'Reyes', 'coach', '2nd Dan, kids program lead'),
            ('sam', 'Sam', 'Okafor', 'coach', '2nd Dan, self-defense'),
        ]
        staff = {}
        for i, (username, first, last, role, _title) in enumerate(people):
            user, _ = User.objects.get_or_create(username=username, defaults={
                'first_name': first, 'last_name': last, 'email': f'{username}@glacierpeak-tkd.example.com'})
            user.set_password(PASSWORD)
            user.save()
            OrganisationMember.objects.create(
                user=user, organisation=org, role=role,
                dbs_number=f'BG-2026-{4100 + i}', dbs_expiry=self.today + timedelta(days=random.randint(-20, 700)),
                coaching_licence=f'KKW-{900000 + i * 137}',
                coaching_licence_expiry=self.today + timedelta(days=random.randint(-30, 900)),
            )
            staff[username] = user
        self._say(f'Staff: {len(staff)} (owner is admin, others are coaches)')
        return staff

    def _belts(self, org):
        from progression.models import ProgressionStage, ProgressionSystem
        system = ProgressionSystem.objects.create(organisation=org, name='Taekwondo Belts',
                                                  assign_to_new_members=True)
        stages = [ProgressionStage.objects.create(system=system, name=name, colour=color,
                                                  order=i + 1, is_default=(i == 0))
                  for i, (name, color) in enumerate(BELTS)]
        self.system = system
        self._say(f'Belts: {len(stages)} ranks')
        return stages

    def _billing(self, org):
        from billing.models import BillingPolicy, PolicyDiscount
        monthly = BillingPolicy.BillingCycle.MONTHLY
        flat = BillingPolicy.PricingModel.FLAT
        policies = {
            'standard': BillingPolicy.objects.create(
                organisation=org, name='Standard (1-year contract)', billing_cycle=monthly, pricing_model=flat,
                amount=130, description='Ages 7 and up, 1-year contract.'),
            'little': BillingPolicy.objects.create(
                organisation=org, name='Little Dragons (6-month contract)', billing_cycle=monthly,
                pricing_model=flat, amount=100, description='Ages 4–6, 6-month contract.'),
            'krav': BillingPolicy.objects.create(
                organisation=org, name='Self-Defense Session', billing_cycle=monthly, pricing_model=flat,
                amount=50, description='Monthly self-defense, gloves not included.'),
        }
        fixed = PolicyDiscount.DiscountType.FIXED
        pct = PolicyDiscount.DiscountType.PERCENTAGE
        self.discounts = {
            2: PolicyDiscount.objects.create(policy=policies['standard'], name='2nd family member', discount_type=fixed, value=30),
            3: PolicyDiscount.objects.create(policy=policies['standard'], name='3rd family member', discount_type=fixed, value=40),
            4: PolicyDiscount.objects.create(policy=policies['standard'], name='4th family member', discount_type=pct, value=50),
            'l2': PolicyDiscount.objects.create(policy=policies['little'], name='2nd child', discount_type=fixed, value=25),
            'l3': PolicyDiscount.objects.create(policy=policies['little'], name='3rd child', discount_type=fixed, value=30),
        }
        self._say('Billing: standard $130, Little Dragons $100, self-defense $50, family discounts')
        return policies

    def _custom_fields(self, org):
        from members.models import CustomField
        fields = {
            'contract': CustomField.objects.create(organisation=org, name='Contract ends',
                                                   field_type=CustomField.FieldType.DATE, order=1),
            'uniform': CustomField.objects.create(organisation=org, name='Uniform size',
                                                  field_type=CustomField.FieldType.SELECT, order=2,
                                                  options=['000', '00', '0', '1', '2', '3', '4', '5', '6']),
            'source': CustomField.objects.create(organisation=org, name='How did you find us?',
                                                 field_type=CustomField.FieldType.SELECT, order=3,
                                                 options=['Facebook ad', 'Google', 'Friend/family', 'Drove by', 'School flyer', 'Instagram']),
            'photo': CustomField.objects.create(organisation=org, name='Photo consent',
                                                field_type=CustomField.FieldType.BOOLEAN, order=4),
        }
        self._say('Custom fields: Contract ends, Uniform size, How did you find us?, Photo consent')
        return fields

    def _classes(self, org, staff):
        from classes.models import Class, ClassCoach
        classes = []
        for name, slots, cap, ages, belts, coaches in CLASSES:
            cls = Class.objects.create(
                organisation=org, name=name, max_capacity=cap, description='',
                schedule=[{'day': d, 'time': t, 'end': e} for d, t, e in slots])
            for key in coaches:
                ClassCoach.objects.create(assigned_class=cls, user=staff[key])
            cls.ages, cls.belts = ages, belts
            classes.append(cls)
        self._say(f'Classes: {len(classes)}')
        return classes

    # ── Students and families ────────────────────────────────────────────────

    def _members(self, org, count, stages, classes, policies, fields, staff):
        from classes.models import ClassMember
        from members.models import FamilyGroup, FamilyGroupMember, Guardian, Member, MemberNote
        from billing.models import MemberDiscount
        from progression.models import MemberProgression

        made, n = [], 0
        while len(made) < count:
            n += 1
            last = random.choice(LAST)
            town, zipcode = random.choice(TOWNS)
            address = f'{random.randint(100, 3999)} {random.choice(STREETS)}'
            household_email = f'{last.lower().replace(" ", "")}.family{n}@example.com'
            parents = [(random.choice(FIRST_ADULTS), random.choice(['Mother', 'Father']))]
            if chance(0.45):
                parents.append((random.choice(FIRST_ADULTS), 'Mother' if parents[0][1] == 'Father' else 'Father'))

            # A household: mostly kids (1–4 siblings), sometimes a parent trains too, sometimes adults only.
            roll = random.random()
            if roll < 0.62:
                kids, adults = random.choices([1, 2, 3, 4], weights=[55, 30, 11, 4])[0], (1 if chance(0.12) else 0)
            else:
                kids, adults = 0, random.choices([1, 2], weights=[80, 20])[0]

            household = []
            for k in range(kids):
                age = random.choices(range(4, 18), weights=[6, 8, 8, 9, 9, 9, 8, 8, 7, 6, 5, 4, 3, 2])[0]
                household.append((random.choice(FIRST_KIDS), age, True))
            for a in range(adults):
                first = parents[a][0] if a < len(parents) and kids else random.choice(FIRST_ADULTS)
                household.append((first, random.randint(18, 68), False))

            fam = []
            for first, age, is_kid in household:
                if len(made) >= count:
                    break
                dob = self.today - timedelta(days=age * 365 + random.randint(0, 364))
                tenure_days = random.choices([60, 200, 400, 800, 1500, 2600], weights=[22, 22, 20, 18, 12, 6])[0]
                tenure_days = min(random.randint(14, tenure_days), max(30, (age - 3) * 365))
                joined = self.today - timedelta(days=tenure_days)
                belt = min(len(stages) - 1, int(tenure_days / 150) + random.randint(-1, 1))
                if age < 7:
                    belt = min(belt, 5)
                belt = max(0, belt)
                little = age <= 6
                policy = policies['little'] if little else policies['standard']
                member = Member.objects.create(
                    organisation=org, name=f'{first} {last}', date_of_birth=dob,
                    email='' if is_kid and age < 13 else f'{first.lower()}.{last.lower().replace(" ", "")}{n}@example.com',
                    phone='' if is_kid else phone(n + len(fam)),
                    address_line1=address, address_line2=f'{town}, MT {zipcode}',
                    emergency_contact_name=f'{parents[0][0]} {last}' if is_kid else f'{random.choice(FIRST_ADULTS)} {last}',
                    emergency_contact_phone=phone(n * 3),
                    emergency_contact_2_name=f'{parents[1][0]} {last}' if is_kid and len(parents) > 1 else '',
                    emergency_contact_2_phone=phone(n * 7) if is_kid and len(parents) > 1 else '',
                    medical_info=random.choice(MEDICAL) if chance(0.14) else '',
                    monthly_fee=policy.amount, billing_policy=policy, joined_date=joined, is_active=True,
                    licence_number=f'USAT-{random.randint(100000, 999999)}' if chance(0.15) else '',
                    custom_field_values={
                        str(fields['contract'].pk): (joined + timedelta(days=182 if little else 365)
                                                     + timedelta(days=365 * (tenure_days // 365))).isoformat(),
                        str(fields['uniform'].pk): random.choice(fields['uniform'].options[:5] if is_kid else fields['uniform'].options[3:]),
                        str(fields['source'].pk): random.choice(fields['source'].options),
                        str(fields['photo'].pk): chance(0.8),
                    },
                )
                if is_kid:
                    for p_first, relation in parents:
                        Guardian.objects.create(member=member, name=f'{p_first} {last}', relationship=relation,
                                                email=household_email if relation == parents[0][1] else
                                                f'{p_first.lower()}.{last.lower().replace(" ", "")}{n}@example.com',
                                                phone=phone(n * 3 if relation == parents[0][1] else n * 7))

                # Belt history: one entry per rank up to the current one.
                when = joined
                gap = max(30, tenure_days // (belt + 1))
                for i in range(belt + 1):
                    MemberProgression.objects.create(member=member, stage=stages[i], achieved_date=min(when, self.today))
                    when += timedelta(days=gap + random.randint(-10, 10))

                # Classes that fit their age and belt; most take one, some take two.
                fits = [c for c in classes[:7] if c.ages[0] <= age <= c.ages[1] and c.belts[0] <= belt <= c.belts[1]]
                picks = fits[:1] if fits else [classes[5]]
                if belt >= 10 and chance(0.7):
                    picks.append(classes[7])  # Black Belt Club
                if age >= 8 and belt >= 4 and chance(0.12):
                    picks.append(classes[8])  # Competition Team
                if age >= 12 and chance(0.08):
                    picks.append(classes[9])  # Self-defense
                for cls in set(picks):
                    ClassMember.objects.create(assigned_class=cls, member=member)

                if chance(0.18):
                    MemberNote.objects.create(member=member, author=random.choice(list(staff.values())),
                                              body=random.choice(NOTES))
                fam.append(member)
                made.append(member)

            # Family group + sibling discounts for households with 2+ students.
            if len(fam) >= 2:
                group = FamilyGroup.objects.create(organisation=org, name=f'{last} Family')
                for pos, member in enumerate(fam, start=1):
                    FamilyGroupMember.objects.create(family_group=group, member=member)
                    key = ('l2' if pos == 2 else 'l3') if member.billing_policy == policies['little'] and pos in (2, 3) \
                        else (min(pos, 4) if pos >= 2 and member.billing_policy == policies['standard'] else None)
                    if key:
                        MemberDiscount.objects.create(member=member, discount=self.discounts[key])

        kids = sum(1 for m in made if m.guardians.exists())
        self._say(f'Students: {len(made)} ({kids} kids with parents, {len(made) - kids} adults)')
        return made

    # ── Attendance ───────────────────────────────────────────────────────────

    def _attendance(self, classes, weeks):
        from classes.models import Attendance, ClassMember, Session
        closures = {self.today - timedelta(days=d) for d in random.sample(range(7, weeks * 7), k=min(6, weeks))}
        sessions = attendance = 0
        for cls in classes:
            enrolled = list(ClassMember.objects.filter(assigned_class=cls).values_list('member_id', flat=True))
            # Each student has their own habit: some never miss, some drift off.
            habit = {mid: random.choice([0.95, 0.9, 0.85, 0.75, 0.6, 0.35]) for mid in enrolled}
            rows = []
            for week in range(-weeks, 3):
                for slot in cls.schedule:
                    day = self.today + timedelta(weeks=week, days=(slot['day'] - self.today.weekday()) % 7)
                    if day > self.today + timedelta(days=14):
                        continue
                    past = day < self.today
                    cancelled = past and (day in closures or chance(0.02))
                    session = Session.objects.create(
                        assigned_class=cls, date=day, is_cancelled=cancelled,
                        notes=random.choice(['Forms review.', 'Sparring drills.', 'Board breaking prep for testing.',
                                             'Kicking drills on pads.', 'Self-defense techniques.', ''])
                        if past and not cancelled and chance(0.3) else '')
                    sessions += 1
                    if past and not cancelled:
                        rows += [Attendance(session=session, member_id=mid, present=chance(habit[mid])) for mid in enrolled]
            Attendance.objects.bulk_create(rows, batch_size=2000)
            attendance += len(rows)
        self._say(f'Sessions: {sessions}, attendance records: {attendance}')

    # ── Invoices and payments ────────────────────────────────────────────────

    def _invoices(self, org, members):
        from billing.models import Invoice, Payment
        invoices, payments = [], []
        first_of_month = self.today.replace(day=1)
        for months_ago in range(6, -1, -1):
            start = (first_of_month - timedelta(days=months_ago * 30)).replace(day=1)
            period = start.strftime('%B %Y')
            due = start.replace(day=10)
            for member in members:
                if member.joined_date and member.joined_date > due:
                    continue
                discount = Decimal('0')
                for md in member.discounts.select_related('discount'):
                    d = md.discount
                    discount += d.value if d.discount_type == 'fixed' else (member.monthly_fee * d.value / 100)
                amount = max(Decimal('0'), Decimal(member.monthly_fee) - discount)
                if due < self.today - timedelta(days=45):
                    status = 'paid' if chance(0.97) else 'overdue'
                elif due < self.today:
                    status = random.choices(['paid', 'overdue', 'unpaid'], weights=[80, 12, 8])[0]
                else:
                    status = 'unpaid'
                inv = Invoice(organisation=org, member=member, billing_policy=member.billing_policy,
                              amount=amount, discount_amount=discount, period=period, due_date=due, status=status)
                invoices.append(inv)
        Invoice.objects.bulk_create(invoices, batch_size=1000)
        # MySQL doesn't return ids from bulk_create, so read the paid ones back.
        for inv in Invoice.objects.filter(organisation=org, status='paid'):
            paid_on = inv.due_date - timedelta(days=random.randint(-12, 9))
            payments.append(Payment(
                invoice=inv, amount=inv.amount,
                method=random.choices(['cash', 'check', 'bacs', 'manual'], weights=[25, 35, 30, 10])[0],
                paid_at=timezone.make_aware(datetime.combine(paid_on, datetime.min.time()) + timedelta(hours=17)),
                notes=f'Check #{random.randint(1001, 9999)}' if chance(0.3) else ''))
        Payment.objects.bulk_create(payments, batch_size=1000)
        self._say(f'Invoices: {len(invoices)} over 7 months, payments: {len(payments)}')

    # ── Belt tests ───────────────────────────────────────────────────────────

    def _gradings(self, org, stages, members):
        from progression.models import Grading, GradingCandidate, GradingSession
        current = {m.pk: m.progressions.order_by('-stage__order').first() for m in members}
        made = 0
        for i, weeks_ago in enumerate([20, 12, 4, -2]):
            day = self.today - timedelta(weeks=weeks_ago)
            day += timedelta(days=(5 - day.weekday()) % 7)  # Saturday
            grading = Grading.objects.create(organisation=org, system=self.system,
                                             name=f'Belt Test, {day:%B %Y}',
                                             notes='Forms, one-steps, sparring and board breaks.')
            for label in ('Juniors', 'Teens & Adults'):
                session = GradingSession.objects.create(grading=grading, name=label, date=day)
                pool = [m for m in members if (m.guardians.exists()) == (label == 'Juniors')]
                for member in random.sample(pool, k=min(len(pool), random.randint(15, 30))):
                    prog = current.get(member.pk)
                    order = prog.stage.order if prog else 1
                    if order >= len(stages) - 2:
                        continue
                    if weeks_ago < 0:
                        result = GradingCandidate.Result.PENDING
                    else:
                        result = random.choices(['passed', 'failed', 'absent'], weights=[85, 9, 6])[0]
                    GradingCandidate.objects.get_or_create(
                        session=session, member=member,
                        defaults={'target_stage': stages[order], 'result': result,
                                  'notes': 'Retest forms next cycle.' if result == 'failed' else ''})
                    made += 1
        self._say(f'Belt tests: 3 past + 1 upcoming, {made} candidates')

    # ── Former students, sign-ups waiting, announcements ─────────────────────

    def _former_members(self, org, count):
        from members.models import Member
        reasons = ['Moved to Missoula.', 'Switched to hockey.', 'Schedule conflict with school sports.',
                   'Cost.', 'Lost interest.', 'Moved out of state.', '']
        for i in range(count):
            first, last = random.choice(FIRST_KIDS + FIRST_ADULTS), random.choice(LAST)
            joined = self.today - timedelta(days=random.randint(400, 2500))
            left = joined + timedelta(days=random.randint(90, 700))
            Member.objects.create(
                organisation=org, name=f'{first} {last}', is_active=False,
                date_of_birth=self.today - timedelta(days=random.randint(6, 50) * 365),
                email=f'former{i}.{last.lower().replace(" ", "")}@example.com', joined_date=joined,
                archived_at=timezone.make_aware(datetime.combine(min(left, self.today), datetime.min.time())),
                retention_notes=random.choice(reasons))
        self._say(f'Former students: {count}')

    def _applications(self, org):
        from members.models import MemberApplication
        for i in range(8):
            last = random.choice(LAST)
            kid = chance(0.7)
            town, zipcode = random.choice(TOWNS)
            MemberApplication.objects.create(
                organisation=org, name=f'{random.choice(FIRST_KIDS if kid else FIRST_ADULTS)} {last}',
                date_of_birth=self.today - timedelta(days=random.randint(5, 12 if kid else 45) * 365),
                email=f'newsignup{i}@example.com', phone=phone(60 + i),
                address_line1=f'{random.randint(100, 3999)} {random.choice(STREETS)}',
                city=town, county='MT', postcode=zipcode,
                guardian_name=f'{random.choice(FIRST_ADULTS)} {last}' if kid else '',
                guardian_email=f'parent{i}@example.com' if kid else '',
                guardian_phone=phone(70 + i) if kid else '',
                medical_info=random.choice(MEDICAL) if chance(0.2) else '',
                notes=random.choice(['Saw your Facebook ad!', 'Want to try a class first.', '', 'Friend trains here.']))
        self._say('Sign-ups waiting for approval: 8')

    def _announcements(self, org, staff):
        from organisations.models import Announcement
        items = [
            (60, 'Closed Labor Day', 'No classes Monday for Labor Day. See you Tuesday!', 'All active members'),
            (40, 'Belt test sign-ups open', 'Sign-up sheet is at the front desk. Test fee is $45.', 'All active members'),
            (21, 'No Little Dragons Thursday', 'Little Dragons is cancelled Thursday. Regular schedule next week.', 'Class: Little Dragons (4–6) T/Th'),
            (10, 'Tournament volunteers needed', 'We need scorekeepers and ring coordinators for the fall tournament.', 'All active members'),
            (3, 'Competition team practice moved', 'Saturday practice starts at 10 this week.', 'Class: Competition Team'),
        ]
        for days_ago, subject, body, label in items:
            Announcement.objects.create(organisation=org, subject=subject, body=body, sent_by=staff['owner'],
                                        sent_at=timezone.now() - timedelta(days=days_ago),
                                        recipient_count=random.randint(40, 280), recipient_label=label)
        self._say(f'Announcements: {len(items)}')
