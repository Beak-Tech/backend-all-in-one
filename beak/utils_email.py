from django.shortcuts import render
from django.core.mail import send_mail

def email_contact(request):
    if request.method == "POST":
        subject = request.POST['subject']
        message = request.POST['link']
        from_email = request.POST['from_email']
        recipient_list = request.POST['recipient_list']


    send_mail(
        subject,
        message,
        from_email,
        recipient_list
        )

    return render(request)