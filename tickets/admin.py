from django.contrib import admin
from .models import Train, Booking, Passenger, Wagon


# Train (მატარებლის) მოდელის რეგისტრაცია ადმინ-პანელში დეკორატორის გამოყენებით
@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    # სვეტები, რომლებიც გამოჩნდება მატარებლების მთავარ სიაში
    list_display = ('id', 'name', 'departure_station', 'arrival_station', 'departure_date', 'departure_time', 'arrival_time')
    # მარჯვენა მხარეს გამოსატანი ფილტრები სწრაფი გაფილტვრისთვის
    list_filter = ('departure_station', 'arrival_station', 'departure_date')
    # ველები, რომელთა მიხედვითაც იმუშავებს საძიებო ველი (Search bar)
    search_fields = ('name', 'departure_station', 'arrival_station')


# დამხმარე კლასი: საშუალებას იძლევა მგზავრები (Passenger) გამოჩნდნენ და დარედაქტირდნენ
# პირდაპირ ჯავშნის (Booking) გვერდის შიგნით, ცხრილის (Tabular) სახით
class PassengerInline(admin.TabularInline):
    model = Passenger
    # extra = 0 ნიშნავს, რომ ავტომატურად არ დაამატოს ცარიელი სტრიქონები ახალი მგზავრისთვის (მხოლოდ ღილაკზე დაჭერისას)
    extra = 0


# Booking (ჯავშნის) მოდელის რეგისტრაცია და მორგება
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # ჯავშნების სიაში გამოსატანი ძირითადი ინფორმაცია
    list_display = ('booking_code', 'train', 'travel_date', 'email', 'phone', 'created_at')
    # ფილტრაცია მგზავრობისა და ჯავშნის შექმნის თარიღების მიხედვით
    list_filter = ('travel_date', 'created_at')
    # ძიება ჯავშნის კოდით, ელფოსტით ან ტელეფონის ნომრით
    search_fields = ('booking_code', 'email', 'phone')
    # ჯავშნის დეტალურ გვერდზე ქვემოთ მიებმება ამ ჯავშანთან დაკავშირებული მგზავრების ცხრილი
    inlines = [PassengerInline]


# Passenger (მგზავრის) მოდელის დამოუკიდებელი რეგისტრაცია ადმინ-პანელში
@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    # მგზავრების სიაში გამოსატანი სვეტები
    list_display = ('first_name', 'last_name', 'personal_id', 'seat_number', 'booking')
    # ძიება სახელით, გვარით ან პირადი ნომრით
    search_fields = ('first_name', 'last_name', 'personal_id')


# Wagon (ვაგონის) მოდელის რეგისტრაცია ადმინ-პანელში
@admin.register(Wagon)
class WagonAdmin(admin.ModelAdmin):
    # ვაგონების სიაში გამოსატანი სვეტები (რომელ მატარებელს ეკუთვნის, ნომერი, ტიპი, ფასი)
    list_display = ('train', 'number', 'wagon_type', 'price')
    # ფილტრაცია კონკრეტული მატარებლისა და ვაგონის ტიპის მიხედვით
    list_filter = ('train', 'wagon_type')