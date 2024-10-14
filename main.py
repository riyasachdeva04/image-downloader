import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

def download_images(keyword, num_images):
    search_url = f"https://unsplash.com/s/photos/{keyword}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'lxml')

    images = soup.find_all('img', {'srcset': True})
    image_urls = [img['src'] for img in images[:num_images]]

    if not image_urls:
        return []

    downloaded_images = []
    for idx, img_url in enumerate(image_urls):
        img_data = requests.get(img_url).content
        img_name = f"{keyword}_{idx + 1}.jpg"
        with open(img_name, 'wb') as img_file:
            img_file.write(img_data)
        downloaded_images.append(img_name)

    return downloaded_images

def send_email(to_email, subject, body, attachments):
    from_email = "sachdevar919@gmail.com"  # Replace with your email
    from_password = "tgpg jelk npas ovvr"  # Replace with your email password

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach images
    for attachment in attachments:
        with open(attachment, 'rb') as file:
            part = MIMEText(file.read(), 'base64', 'utf-8')
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment)}"')
            msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    keyword = request.form['keyword']
    num_images = int(request.form['num_images'])
    email = request.form['email']

    # Download images
    downloaded_images = download_images(keyword, num_images)

    if not downloaded_images:
        return f"Unfortunately, no images could be downloaded for the keyword '{keyword}'. Please try another keyword."

    # Send email with downloaded images
    send_email(email, f'Images for "{keyword}"', 'Here are your images:', downloaded_images)

    return f'Images for "{keyword}" have been downloaded and sent to {email}.'

if __name__ == '__main__':
    app.run(debug=True)
