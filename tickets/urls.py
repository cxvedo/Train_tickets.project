from django.urls import path
from . import views

# აპლიკაციის URL მარშრუტების (მისამართების) სია
urlpatterns = [
    # მთავარი გვერდი (საწყისი მისამართი)
    path('', views.index_view, name='home'),
    
    # ბილეთის დაჯავშნის გვერდი (მგზავრებისა და ადგილების არჩევა)
    path('booking/', views.book_ticket, name='book_ticket'),
    
    # მატარებლების სია და ძიების შედეგების გვერდი
    path('trains/', views.train_list, name='train_list'),
    
    # შეძენილი ბილეთის შემოწმება ჯავშნის კოდით
    path('check-ticket/', views.check_ticket_view, name='check_ticket'),
    
    # ბილეთის გაუქმების გვერდი
    path('cancel-ticket/', views.cancel_ticket_view, name='cancel_ticket'),
    
    # ახალი მომხმარებლის რეგისტრაციის გვერდი
    path('register/', views.register_view, name='register'),
    
    # სისტემაში შესვლის (ავტორიზაციის) გვერდი
    path('login/', views.login_view, name='login'),
    
    # სისტემიდან გასვლის მისამართი
    path('logout/', views.logout_view, name='logout'),
    
    # გადახდის გვერდი (URL-ში გადაეცემა კონკრეტული ჯავშნის ID მთელი რიცხვის სახით)
    path('payment/<int:booking_id>/', views.payment_view, name='payment_page'),
    
    # შეძენილი ბილეთის დეტალური ნახვა (URL-ში გადაეცემა ჯავშნის ID)
    path('ticket/<int:booking_id>/', views.ticket_detail, name='ticket_detail'),
]