# listings/serializers.py
from rest_framework import serializers
from .models import Listing, Booking, Review # Importez tous les modèles nécessaires
from django.contrib.auth import get_user_model # Pour obtenir le modèle User configuré

User = get_user_model() # Obtenez le modèle User actif

class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur simple pour représenter l'hôte/invité."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name'] # Adaptez selon votre modèle User

class ReviewSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Review."""
    guest = UserSerializer(read_only=True) # Affiche les détails de l'invité

    class Meta:
        model = Review
        fields = ['id', 'listing', 'guest', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

class ListingSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Listing."""
    host = UserSerializer(read_only=True) # Pour afficher les détails de l'hôte
    # Vous pouvez également imbriquer les critiques et les réservations si vous voulez les afficher directement avec le logement
    reviews = ReviewSerializer(many=True, read_only=True) # Affiche les critiques associées
    bookings_count = serializers.SerializerMethodField() # Un champ personnalisé

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price_per_night', 'number_of_rooms',
            'max_guests', 'city', 'country', 'host', 'reviews', 'bookings_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_bookings_count(self, obj):
        """Retourne le nombre de réservations pour ce logement."""
        return obj.bookings.count()

class BookingSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Booking."""
    listing = ListingSerializer(read_only=True) # Affiche les détails du logement
    guest = UserSerializer(read_only=True) # Affiche les détails de l'invité

    # Vous pouvez ajouter des champs write-only si vous voulez accepter des IDs
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source='listing', write_only=True
    )
    guest_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='guest', write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_id', 'guest', 'guest_id', 'check_in_date',
            'check_out_date', 'total_price', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'status', 'created_at', 'updated_at']

    # Surcharger create ou update si le calcul du total_price est complexe ou basé sur la logique de l'API
    def validate(self, data):
        # Exemple de validation pour s'assurer que check_out_date est après check_in_date
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date.")
        return data

    def create(self, validated_data):
        # Calculez le prix total ici, si ce n'est pas fait côté client
        listing = validated_data.get('listing')
        check_in = validated_data.get('check_in_date')
        check_out = validated_data.get('check_out_date')
        if listing and check_in and check_out:
            import datetime
            delta = check_out - check_in
            validated_data['total_price'] = listing.price_per_night * delta.days
        return super().create(validated_data)