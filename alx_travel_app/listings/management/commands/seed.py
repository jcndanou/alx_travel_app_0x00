# listings/management/commands/seed.py
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from alx_travel_app.listings.models import Listing, Booking, Review  # Modifié

User = get_user_model() # Obtenez le modèle User actif

class Command(BaseCommand):
    help = 'Populates the database with sample listings, bookings, and reviews.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # 1. Créer quelques utilisateurs de test si nécessaire
        if not User.objects.exists():
            self.stdout.write('Creating sample users...')
            users_data = [
                {'username': 'host1', 'email': 'host1@example.com', 'password': 'password123', 'first_name': 'Alice', 'last_name': 'Host', 'is_staff': True},
                {'username': 'guest1', 'email': 'guest1@example.com', 'password': 'password123', 'first_name': 'Bob', 'last_name': 'Guest'},
                {'username': 'guest2', 'email': 'guest2@example.com', 'password': 'password123', 'first_name': 'Charlie', 'last_name': 'Guest'},
            ]
            for data in users_data:
                user = User.objects.create_user(
                    email=data['email'],
                    password=data['password'],
                    username=data['username'], # Si votre User a un username
                    first_name=data['first_name'],
                    last_name=data['last_name']
                )
                if data.get('is_staff'):
                    user.is_staff = True
                    user.save()
            self.stdout.write(self.style.SUCCESS('Sample users created.'))
        else:
            self.stdout.write('Users already exist, skipping user creation.')

        hosts = User.objects.filter(is_staff=True)
        guests = User.objects.filter(is_staff=False)

        if not hosts.exists() or not guests.exists():
            self.stdout.write(self.style.WARNING('Not enough hosts/guests. Please create at least one staff user and one regular user.'))
            return

        # 2. Créer des Listings
        if not Listing.objects.exists():
            self.stdout.write('Creating sample listings...')
            listings_data = [
                {
                    'title': 'Cozy Apartment in City Center',
                    'description': 'A beautiful apartment close to all amenities.',
                    'price_per_night': 75.00,
                    'number_of_rooms': 2,
                    'max_guests': 4,
                    'city': 'Paris',
                    'country': 'France',
                    'host': random.choice(hosts)
                },
                {
                    'title': 'Spacious Villa with Pool',
                    'description': 'Perfect for a family getaway.',
                    'price_per_night': 200.00,
                    'number_of_rooms': 5,
                    'max_guests': 10,
                    'city': 'Nice',
                    'country': 'France',
                    'host': random.choice(hosts)
                },
                {
                    'title': 'Beachfront Bungalow',
                    'description': 'Wake up to the sound of waves.',
                    'price_per_night': 150.00,
                    'number_of_rooms': 3,
                    'max_guests': 6,
                    'city': 'Marseille',
                    'country': 'France',
                    'host': random.choice(hosts)
                },
            ]
            for data in listings_data:
                Listing.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f'{len(listings_data)} listings created.'))
        else:
            self.stdout.write('Listings already exist, skipping listing creation.')

        listings = Listing.objects.all()

        # 3. Créer des Bookings
        if not Booking.objects.exists() and listings.exists() and guests.exists():
            self.stdout.write('Creating sample bookings...')
            today = date.today()
            bookings_created = 0
            for _ in range(5): # Créer 5 réservations aléatoires
                listing = random.choice(listings)
                guest = random.choice(guests)
                check_in_date = today + timedelta(days=random.randint(1, 30))
                check_out_date = check_in_date + timedelta(days=random.randint(2, 7))
                total_price = listing.price_per_night * (check_out_date - check_in_date).days

                try:
                    Booking.objects.create(
                        listing=listing,
                        guest=guest,
                        check_in_date=check_in_date,
                        check_out_date=check_out_date,
                        total_price=total_price,
                        status=random.choice(['pending', 'confirmed'])
                    )
                    bookings_created += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not create booking: {e}')) # Peut échouer à cause d'unique_together
            self.stdout.write(self.style.SUCCESS(f'{bookings_created} bookings created.'))
        else:
            self.stdout.write('Bookings already exist or no listings/guests, skipping booking creation.')

        # 4. Créer des Reviews
        if not Review.objects.exists() and listings.exists() and guests.exists():
            self.stdout.write('Creating sample reviews...')
            reviews_created = 0
            for _ in range(3): # Créer 3 avis aléatoires
                listing = random.choice(listings)
                guest = random.choice(guests)
                try:
                    Review.objects.create(
                        listing=listing,
                        guest=guest,
                        rating=random.randint(1, 5),
                        comment=f"Great stay at {listing.title}!" if random.random() > 0.5 else None
                    )
                    reviews_created += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not create review: {e}')) # Peut échouer à cause d'unique_together
            self.stdout.write(self.style.SUCCESS(f'{reviews_created} reviews created.'))
        else:
            self.stdout.write('Reviews already exist or no listings/guests, skipping review creation.')

        self.stdout.write(self.style.SUCCESS('Database seeding completed.'))