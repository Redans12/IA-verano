from googleapiclient.discovery import build

API_KEY = "AIzaSyCTNOrhpuBxpBrupkol--H50EYfbcMQgZE"
VIDEO_ID = "Jy6kb4AopBA"  # lo sacas de la URL, después de watch?v=

youtube = build("youtube", "v3", developerKey=API_KEY)

comentarios = []
request = youtube.commentThreads().list(
    part="snippet",
    videoId=VIDEO_ID,
    maxResults=100,
    textFormat="plainText"
)

while request and len(comentarios) < 30:
    response = request.execute()
    for item in response["items"]:
        c = item["snippet"]["topLevelComment"]["snippet"]
        comentarios.append({
            "autor": c["authorDisplayName"],
            "texto": c["textDisplay"],
            "fecha": c["publishedAt"],
            "likes": c["likeCount"]
        })
    request = youtube.commentThreads().list_next(request, response)

import pandas as pd
df = pd.DataFrame(comentarios[:30])
df.to_csv("comentarios_youtube_voto.csv", index=False)
print(f"Guardados {len(df)} comentarios")