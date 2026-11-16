from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from tickets.forms import TrainSearchForm
from .models import Train, Booking, Passenger, Wagon
import datetime
from django.contrib.auth.decorators import login_required


# მთავარი გვერდის (Index) გამოსახვა
def index_view(request):
    # მატარებლების საძიებო ფორმის ინიციალიზაცია (GET მონაცემებით ან ცარიელი)
    form = TrainSearchForm(request.GET or None)
    # ბაზიდან ყველა მატარებლის წამოღება
    trains = Train.objects.all()
    context = {'form': form, 'trains': trains}
    return render(request, 'tickets/index.html', context)


# მომხმარებლის რეგისტრაციის ლოგიკა
def register_view(request):
    if request.method == 'POST':
        # ფორმის შევსება მომხმარებლის მიერ გამოგზავნილი მონაცემებით
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # ახალი მომხმარებლის ბაზაში შენახვა
            user = form.save()
            # რეგისტრაციისთანავე სისტემაში ავტომატური შესვლა (ავტორიზაცია)
            login(request, user)
            messages.success(request, "რეგისტრაცია წარმატებით დასრულდა!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'tickets/register.html', {'form': form})


# სისტემაში ავტორიზაციის ლოგიკა
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # მომხმარებლის სახელისა და პაროლის გადამოწმება ბაზასთან
            user = authenticate(
                username=form.cleaned_data.get('username'), 
                password=form.cleaned_data.get('password')
            )
            if user is not None:
                login(request, user)
            
            # ვიღებთ იმ გვერდის მისამართს, საიდანაც @login_required-მა გადმოგვამისამართა
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                
            return redirect('home')
        # შეცდომის შეტყობინება, თუ მონაცემები არასწორია
        messages.error(request, "არასწორი სახელი ან პაროლი.")
    else:
        form = AuthenticationForm()
    return render(request, 'tickets/login.html', {'form': form})


# სისტემიდან გასვლის (Logout) ლოგიკა
def logout_view(request):
    logout(request)
    return redirect('home')


# მატარებლების ძიება და გაფილტრვა
def train_list(request):
    # URL-დან (GET პარამეტრებიდან) საძიებო კრიტერიუმების ამოღება
    from_station = request.GET.get('from_station')
    to_station = request.GET.get('to_station')
    departure_date = request.GET.get('departure_date')
    
    trains = Train.objects.all()
    
    # ფილტრაცია გამგზავრების სადგურის მიხედვით (რეგისტრის უგულებელყოფით - icontains)
    if from_station:
        trains = trains.filter(departure_station__icontains=from_station)
    # ფილტრაცია დანიშნულების სადგურის მიხედვით
    if to_station:
        trains = trains.filter(arrival_station__icontains=to_station)
    # ფილტრაცია გამგზავრების ზუსტი თარიღის მიხედვით
    if departure_date:
        trains = trains.filter(departure_date=departure_date)
        
    return render(request, 'tickets/train_list.html', {'trains': trains})


# ვაგონების სტანდარტული სია
DEFAULT_WAGONS = [
    {"n": 1, "type": "პირველი კლასი", "price": 40},
    {"n": 2, "type": "ეკონომ კლასი", "price": 30},
    {"n": 3, "type": "ბიზნეს კლასი", "price": 60},
]


# კონკრეტული მატარებლის ვაგონების წამოღება ბაზიდან
def get_wagons(train):
    items = [
        {"n": w.number, "type": w.get_type_display(), "price": w.price}
        for w in Wagon.objects.filter(train=train)
    ]
    return items or DEFAULT_WAGONS


# ბილეთის დაჯავშნის მთავარი ლოგიკა
def book_ticket(request):
    # მატარებლის ID-ის მიღება GET ან POST მოთხოვნიდან
    train_id = request.GET.get('train_id') or (request.POST.get('train_id') if request.method == 'POST' else None)
    # შესაბამისი მატარებლის პოვნა (თუ ID არ არის, იღებს ბაზაში არსებულ პირველ მატარებელს)
    train = Train.objects.filter(id=train_id).first() if train_id else Train.objects.first()
    # მგზავრობის თარიღის განსაზღვრა (თუ არ არის მითითებული, იღებს დღევანდელ თარიღს)
    departure_date = request.GET.get('date') or request.GET.get('departure_date') or str(datetime.date.today())

    # მგზავრების რაოდენობის წაკითხვა
    try:
        passengers_count = int(request.POST.get('passengers_count') or request.GET.get('passengers', 1))
        if passengers_count < 1: 
            passengers_count = 1
    except ValueError:
        passengers_count = 1

    wagons = get_wagons(train)

    # თუ მომხმარებელმა შეავსო ჯავშნის ფორმა და დააჭირა გაგზავნას
    if request.method == 'POST':
        # 1. იქმნება მთავარი ჯავშნის (Booking) ჩანაწერი ბაზაში
        booking = Booking.objects.create(
            train=train,
            travel_date=request.POST.get('travel_date'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone')
        )
        
        # 2. ციკლით იქმნება თითოეული მგზავრის (Passenger) ჩანაწერი და ებმება ზემოთ შექმნილ ჯავშანს
        for i in range(1, passengers_count + 1):
            seat_val = request.POST.get(f'seat_{i}', '1B')
            wagon_num = str(request.POST.get(f'wagon_{i}', 1))
            
            Passenger.objects.create(
                booking=booking,
                first_name=request.POST.get(f'first_name_{i}'),
                last_name=request.POST.get(f'last_name_{i}'),
                personal_id=request.POST.get(f'personal_id_{i}'),
                wagon_number=wagon_num,
                seat_number=seat_val,
            )

            request.session[f'booking_total_{booking.id}'] = request.POST.get('total_price', 0)

        return redirect('payment_page', booking_id=booking.id)


    # უკვე დაკავებული ადგილების შეგროვება
    taken = {}
    if train:
        for p in Passenger.objects.filter(booking__train=train, booking__travel_date=departure_date):
            taken.setdefault(str(p.wagon_number), []).append(p.seat_number)

    context = {
        'train': train,
        'departure_date': departure_date,
        'passengers_range': range(1, passengers_count + 1), # შაბლონში ციკლის დასატრიალებლად
        'taken_seats': taken,
        'passengers_count': passengers_count,
        'wagons': wagons,
    }
    return render(request, 'tickets/booking.html', context)


# გადახდის გვერდი (ხელმისაწვდომია მხოლოდ ავტორიზებული მომხმარებლებისთვის)
@login_required(login_url='login')
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # 1. ვიღებთ ვაგონების ფასებს: {'1': 40, '2': 30, '3': 60}
    wagons = get_wagons(booking.train)
    wagon_prices = {str(w['n']): w['price'] for w in wagons}
    
    # 2. ვითვლით ჯამს ამ ჯავშანზე მიბმული ყველა მგზავრის ვაგონის ფასით
    total_price = 0
    for p in booking.passengers.all():
        total_price += wagon_prices.get(str(p.wagon_number), 0)

    if request.method == 'POST':
        messages.success(request, "გადახდა წარმატებით დასრულდა!")
        return redirect('ticket_detail', booking_id=booking.id)

    context = {
        'booking': booking,
        'total_price': total_price,
    }
    return render(request, 'tickets/payment.html', context)
# შეძენილი ბილეთის დეტალური ნახვა
def ticket_detail(request, booking_id): 
    booking = get_object_or_404(Booking, id=booking_id)
    # ამ ჯავშანზე მიბმული ყველა მგზავრის წამოღება (related_name='passengers'-ის გამოყენებით)
    passengers = booking.passengers.all()
    
    context = {
        'booking': booking,
        'passengers': passengers,
    }
    return render(request, 'tickets/ticket_detail.html', context)


# ბილეთის შემოწმება ჯავშნის კოდით
def check_ticket_view(request):
    booking, error_message = None, None
    if request.method == 'POST':
        # შეყვანილი კოდის წაკითხვა და ზედმეტი ცარიელი სივრცეების (space) მოშორება
        ticket_code = request.POST.get('ticket_code', '').strip()
        if ticket_code:
            # ძიება კოდის მიხედვით (დიდი/პატარა ასოების განურჩევლად - iexact)
            booking = Booking.objects.filter(booking_code__iexact=ticket_code).first()
            if not booking:
                error_message = "მითითებული ნომრით ბილეთი ვერ მოიძებნა!"
    return render(request, 'tickets/check_ticket.html', {'booking': booking, 'error_message': error_message})


# ბილეთის გაუქმება (ბაზიდან წაშლა)
def cancel_ticket_view(request):
    booking_code = request.GET.get('code')
    # პოულობს ჯავშანს კოდით, ან თუ კოდი არ არის გადმოცემული, იღებს ბოლო ჯავშანს
    booking = Booking.objects.filter(booking_code=booking_code).first() if booking_code else Booking.objects.last()
    
    if request.method == 'POST' and booking:
        # ჯავშნის (და მასზე მიბმული მგზავრების) წაშლა ბაზიდან
        booking.delete()
        messages.success(request, "ბილეთი გაუქმდა!")
        return redirect('home')
        
    return render(request, 'tickets/cancel_ticket.html', {'booking': booking})