import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv


load_dotenv()

TEMPLATE_ID = "d-25feeead2cc04c56afdfccaf437da641"


def send_mail(emails, username, comment, tema, idComment):
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        print("SendGrid API key not found.")
        return

    base_url = "http://localhost:5000"

    print(f"Using API Key: {api_key}")

    for element in emails:
        like_url = f"{base_url}/likeCommentEmail/{idComment}/{element}"
        dislike_url = f"{base_url}/dislikeCommentEmail/{idComment}/{element}"

        html_content = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        background-color: #f4f4f4;
                        color: #333;
                        padding: 20px;
                        line-height: 1.6;
                        text-align: center;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: auto;
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
                    }}
                    h2 {{
                        color: #333;
                    }}
                    p {{
                        margin: 10px 0;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 10px 15px;
                        margin: 10px 5px;
                        border-radius: 5px;
                        background-color: #7f8c8d;
                        color: white;
                        text-decoration: none;
                        transition: background-color 0.3s ease;
                    }}
                    .button:hover {{
                        background-color: #95a5a6;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 0.8em;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Forum Notification</h2>
                    <p><strong>Comment ID:</strong> {idComment}</p>
                    <p><strong>Topic:</strong> {tema}</p>
                    <p><strong>By:</strong> {username}</p>
                    <p><strong>Comment:</strong> {comment}</p>
                    <div>
                        <a href="{like_url}" class="button">Upvote</a>
                        <a href="{dislike_url}" class="button">Downvote</a>
                    </div>
                </div>
                <div class="footer">
                    <p>This is an automated message, please do not reply.</p>
                </div>
            </body>
        </html>
        """
        message = Mail(
            from_email="lukazvezda1@gmail.com",
            to_emails=element,
            subject="Forum Message:",
            html_content=html_content,
        )

        try:
            print(message)
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print("Error sending email:")
            print(str(e))


if __name__ == "__main__":
    send_mail()
