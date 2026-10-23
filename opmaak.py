def background_image(image : str):
    bg_img = """
    <style>
    [data-testid="stAppViewContainer"] {
    background-image: url({image});
    background-size: cover;
    }
    </style>
    """
    return bg_img