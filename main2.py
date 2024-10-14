import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, render_template
from bs4 import BeautifulSoup

app = Flask(__name__)

API_KEY = ''  
SEARCH_ENGINE_ID = ''  


def download_images(keyword, num_images):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={keyword}&searchType=image&key={API_KEY}&cx={SEARCH_ENGINE_ID}&num={num_images}"
    response = requests.get(search_url)
    results = response.json()

    image_urls = [item['link'] for item in results['items']]

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
    from_email = ""  
    from_password = ""  

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

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

    downloaded_images = download_images(keyword, num_images)

    if not downloaded_images:
        return f"Unfortunately, no images could be downloaded for the keyword '{keyword}'. Please try another keyword."

    send_email(email, f'Images for "{keyword}"', 'Here are your images:', downloaded_images)

    return f'Images for "{keyword}" have been downloaded and sent to {email}.'


if __name__ == '__main__':
    app.run(debug=True)
