# listings/models.py
from django.db import models
from django.conf import settings # Pour référencer le modèle User configuré (AUTH_USER_MODEL)

class Listing(models.Model):
    """Représente une propriété disponible à la location."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_rooms = models.IntegerField()
    max_guests = models.IntegerField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Utilise le modèle User défini dans settings.py
        on_delete=models.CASCADE,
        related_name='listings'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Booking(models.Model):
    """Représente une réservation pour un logement."""
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Exemple de statut de réservation avec des choix
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Contrainte pour éviter les doubles réservations pour la même annonce et les mêmes dates
        # Vous pouvez ajouter une contrainte d'unicité sur (listing, guest, check_in_date)
        # ou une contrainte plus complexe pour la disponibilité.
        unique_together = ('listing', 'check_in_date', 'check_out_date')


    def __str__(self):
        return f"Booking for {self.listing.title} by {self.guest.username}"

class Review(models.Model):
    """Représente une évaluation laissée par un invité pour un logement."""
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)]) # Notation de 1 à 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Un invité ne peut laisser qu'un seul avis par logement
        unique_together = ('listing', 'guest')

    def __str__(self):
        return f"Review for {self.listing.title} by {self.guest.username} - Rating: {self.rating}"