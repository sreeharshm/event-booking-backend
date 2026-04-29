from django.core.mail import EmailMultiAlternatives


def send_password_reset_email(to_email, otp):
    subject = "Event Booking – Password Reset Code"

    text = f"""
You requested to reset your Event Booking password.

Use this code to reset your password:

OTP: {otp}

This code is valid for 5 minutes.
"""

    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
        <h2 style="color:#2c3e50;">Password Reset Request</h2>
        <p>You requested to reset your <strong>Event Booking</strong> password.</p>
        <p>Use the code below to reset your password:</p>
        <div style="
            margin:20px 0;
            padding:15px;
            background:#f7faff;
            border-radius:10px;
            border:1px solid #dce7ff;
            text-align:center;
        ">
            <span style="font-size:30px; font-weight:bold; letter-spacing:6px; color:#1a73e8;">
                {otp}
            </span>
        </div>
        <p>This code is valid for <strong>5 minutes</strong>.</p>
        <p style="font-size:12px; color:#777; margin-top:20px;">
            If you did not request this, you can safely ignore this email.<br/>
            — Event Booking Team
        </p>
    </div>
    """

    msg = EmailMultiAlternatives(subject, text, None, [to_email])
    msg.attach_alternative(html, "text/html")
    msg.send()