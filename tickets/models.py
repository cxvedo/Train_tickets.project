import uuid
from django.db import models


# მატარებლის რეისის მოდელი
class Train(models.Model):
    # მატარებლის დასახელება ან ტიპი (საწყისი მნიშვნელობაა "Express")
    name = models.CharField(max_length=100, default="Express")
    # გამგზავრებისა და დანიშნულების სადგურები
    departure_station = models.CharField(max_length=100)
    arrival_station = models.CharField(max_length=100)
    # გამგზავრებისა და ჩასვლის დრო
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    departure_date = models.DateField(null=True)
    # ბილეთის საბაზისო ფასი (მაქსიმუმ 6 ციფრი, აქედან 2 ათწილადის შემდეგ)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=35.00)

    # ობიექტის ტექსტური წარმოდგენა (ადმინ-პანელსა და კონსოლში გამოსაჩენად)
    def __str__(self):
        return f"{self.name}: {self.departure_station} -> {self.arrival_station}"


# ჯავშნის (ბილეთის შეკვეთის) მოდელი
class Booking(models.Model):
    # ჯავშნის უნიკალური კოდი (იქმნება ავტომატურად save მეთოდში)
    booking_code = models.CharField(max_length=10, unique=True, blank=True)
    # კავშირი მატარებელთან (მატარებლის წაშლისას წაიშლება მასზე მიბმული ჯავშნებიც)
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='bookings')
    # მგზავრობის თარიღი და საკონტაქტო ინფორმაცია
    travel_date = models.DateField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    # ჯავშნის შექმნის ზუსტი დრო (ივსება ავტომატურად შექმნის მომენტში)
    created_at = models.DateTimeField(auto_now_add=True)

    # სტანდარტული save მეთოდის გადატვირთვა უნიკალური კოდის დასაგენერირებლად
    def save(self, *args, **kwargs):
        if not self.booking_code:
            self.booking_code = "TT-" + uuid.uuid4().hex[:6].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_code} ({self.train})"


# კონკრეტული მგზავრის მოდელი (ერთ ჯავშანს შეიძლება ჰყავდეს რამდენიმე მგზავრი)
class Passenger(models.Model):
    # კავშირი მთავარ ჯავშანთან (related_name='passengers' საშუალებას გვაძლევს გამოვიყენოთ booking.passengers.all())
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # პირადი ნომერი (11 სიმბოლო)
    personal_id = models.CharField(max_length=11)
    # არჩეული ადგილისა და ვაგონის ნომერი
    seat_number = models.CharField(max_length=10)
    wagon_number = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Seat {self.seat_number})"


# ვაგონის მოდელი
class Wagon(models.Model):
    # ვაგონის კლასების ასარჩევი სია (Choices)
    TRAIN_CLASSES = [
        ('1', 'პირველი კლასი'),
        ('2', 'ეკონომ კლასი'),
        ('3', 'ბიზნეს კლასი'),
    ]
    # კავშირი მატარებელთან
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='wagons')
    # ვაგონის რიგითი ნომერი
    number = models.IntegerField(verbose_name="ვაგონის ნომერი")
    wagon_type = models.CharField(max_length=20, choices=TRAIN_CLASSES, default='2', verbose_name="კლასი")
    # კონკრეტულ ვაგონში მგზავრობის ფასი
    price = models.DecimalField(max_digits=6, decimal_places=2, default=30.00, verbose_name="ფასი")

    def __str__(self):
        return f"ვაგონი {self.number} ({self.get_wagon_type_display()}) - {self.price} ლარი"