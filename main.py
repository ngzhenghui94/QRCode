from flask import Flask, request, Response, jsonify
import qrcode
from PIL import Image
import io
import requests

app = Flask(__name__)

@app.route('/qr', methods=['GET'])
def generate_qr():
    url = request.args.get('url')
    logo_url = request.args.get('logo')

    if not url:
        return jsonify(error="Please provide a valid URL as a query parameter"),400

    qr = qrcode.QRCode(version=5, box_size=20, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.convert("RGBA")
    img.putalpha(200)

    if logo_url and "png" in logo_url:
        try:
            logo_data = requests.get(logo_url)
            logo_data.raise_for_status()
            logo = Image.open(io.BytesIO(logo_data.content))
            logo = logo.resize((img.size[0] // 5, img.size[1] // 5))
            logo = logo.convert("RGBA")
            img.paste(logo, (img.size[0] // 2 - logo.size[0] // 2, img.size[1] // 2 - logo.size[1] // 2), logo)
        except:
            return jsonify(error="The logo url provided is not valid or cannot be opened"), 400
    elif logo_url and "png" not in logo_url:
        return jsonify(error="The Logo must be in png format"),400


    #Convert PIL Image to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return Response(img_bytes.getvalue(),content_type='image/png',mimetype='image/png',headers={
                    "Content-Disposition": "attachment;filename=qr.png"})

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8000)
