import base64

def make_img(file : str):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def background_image(img : str):
    plaatje = make_img(img)

    bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{plaatje}");
    background-size: 10%;
    background-position: top right;
    background-repeat: no-repeat;
    }}
    </style>
    """
    return bg_img